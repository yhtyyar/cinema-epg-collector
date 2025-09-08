"""
Упрощенная система умного управления EPG данными.
Фокус на работоспособности и простоте.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from .config import Config
from .iptv_api import fetch_epg as _original_fetch_epg

logger = logging.getLogger(__name__)


class SimpleEPGManager:
    """Упрощенный менеджер EPG с инкрементальным обновлением."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_epg_file = self.data_dir / "raw_epg.json"
        self.metadata_file = self.data_dir / "epg_smart_metadata.json"
        
        # Настройки
        self.default_past_days = 7
        self.default_future_days = 14
        self.cleanup_days = 30
    
    def should_update_epg(self) -> tuple[bool, str]:
        """
        Определяет нужно ли обновлять EPG данные.
        
        Returns:
            (should_update, reason)
        """
        if not self.raw_epg_file.exists():
            return True, "Файл EPG не существует"
        
        if not self.metadata_file.exists():
            return True, "Метаданные отсутствуют"
        
        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            last_update_str = metadata.get('last_update')
            if not last_update_str:
                return True, "Нет информации о последнем обновлении"
            
            last_update = datetime.fromisoformat(last_update_str)
            hours_since_update = (datetime.now() - last_update).total_seconds() / 3600
            
            # Обновляем если прошло больше 6 часов
            if hours_since_update > 6:
                return True, f"Прошло {hours_since_update:.1f} часов с последнего обновления"
            
            # Проверяем покрытие дат
            coverage = metadata.get('date_coverage', {})
            if not coverage:
                return True, "Нет информации о покрытии дат"
            
            coverage_start = datetime.fromisoformat(coverage['start']).date()
            coverage_end = datetime.fromisoformat(coverage['end']).date()
            
            today = datetime.now().date()
            target_start = today - timedelta(days=self.default_past_days)
            target_end = today + timedelta(days=self.default_future_days)
            
            # Проверяем нужны ли новые данные
            if coverage_start > target_start:
                return True, f"Нужны данные с {target_start} (есть с {coverage_start})"
            
            if coverage_end < target_end:
                return True, f"Нужны данные до {target_end} (есть до {coverage_end})"
            
            return False, "Данные актуальны"
            
        except Exception as e:
            logger.warning(f"Ошибка проверки метаданных: {e}")
            return True, f"Ошибка проверки: {e}"
    
    def get_optimal_request_params(self) -> Dict[str, str]:
        """Возвращает оптимальные параметры для запроса EPG."""
        today = datetime.now().date()
        
        # Определяем нужный диапазон
        start_date = today - timedelta(days=self.default_past_days)
        end_date = today + timedelta(days=self.default_future_days)
        
        # Если есть существующие данные, оптимизируем запрос
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                coverage = metadata.get('date_coverage', {})
                if coverage:
                    existing_start = datetime.fromisoformat(coverage['start']).date()
                    existing_end = datetime.fromisoformat(coverage['end']).date()
                    
                    # Расширяем диапазон только в нужную сторону
                    if existing_start <= start_date and existing_end >= end_date:
                        # Данные полностью покрывают нужный диапазон
                        # Запрашиваем минимум для обновления
                        start_date = today - timedelta(days=1)
                        end_date = today + timedelta(days=2)
                    elif existing_end >= today:
                        # Есть данные на будущее, запрашиваем только прошлое
                        end_date = min(end_date, existing_end)
                    elif existing_start <= today:
                        # Есть данные на прошлое, запрашиваем только будущее
                        start_date = max(start_date, existing_start)
                        
            except Exception as e:
                logger.warning(f"Ошибка оптимизации запроса: {e}")
        
        # Вычисляем параметры относительно сегодняшнего дня
        days_from_today_start = (start_date - today).days
        days_total = (end_date - start_date).days + 1
        
        return {
            "epg_from": str(days_from_today_start),
            "epg_limit": str(days_total)
        }
    
    def merge_epg_data(self, existing_data: List[Dict], new_data: List[Dict]) -> List[Dict]:
        """Объединяет EPG данные по дням."""
        logger.info(f"Объединение EPG: {len(existing_data)} существующих дней + {len(new_data)} новых")
        
        # Индексируем существующие данные по дате
        existing_by_date = {}
        for day in existing_data:
            date_key = day.get('date', '')
            if date_key:
                existing_by_date[date_key] = day
        
        # Добавляем/обновляем новые данные
        updated_count = 0
        added_count = 0
        
        for new_day in new_data:
            date_key = new_day.get('date', '')
            if not date_key:
                continue
                
            if date_key in existing_by_date:
                # Обновляем существующий день
                existing_by_date[date_key] = new_day
                updated_count += 1
            else:
                # Добавляем новый день
                existing_by_date[date_key] = new_day
                added_count += 1
        
        # Фильтруем устаревшие данные
        cutoff_date = datetime.now() - timedelta(days=self.cleanup_days)
        filtered_data = []
        removed_count = 0
        
        for day in existing_by_date.values():
            try:
                date_str = day.get('date', '')
                if date_str:
                    # Парсим дату в формате DD.MM.YYYY
                    day_date = datetime.strptime(date_str, '%d.%m.%Y')
                    if day_date >= cutoff_date:
                        filtered_data.append(day)
                    else:
                        removed_count += 1
                else:
                    filtered_data.append(day)
            except ValueError:
                # Если не удалось распарсить дату, сохраняем день
                filtered_data.append(day)
        
        # Сортируем по дате
        filtered_data.sort(key=lambda x: self._parse_date_key(x.get('date', '')))
        
        logger.info(f"Объединение завершено: добавлено {added_count}, обновлено {updated_count}, "
                   f"удалено устаревших {removed_count}, итого {len(filtered_data)} дней")
        
        return filtered_data
    
    def _parse_date_key(self, date_str: str) -> datetime:
        """Парсит дату из строки для сортировки."""
        try:
            return datetime.strptime(date_str, '%d.%m.%Y')
        except ValueError:
            return datetime.min
    
    def analyze_data_coverage(self, epg_data: List[Dict]) -> Dict[str, Any]:
        """Анализирует покрытие данных."""
        if not epg_data:
            return {
                'start': None,
                'end': None,
                'days_count': 0,
                'programs_count': 0
            }
        
        dates = []
        total_programs = 0
        
        for day in epg_data:
            date_str = day.get('date', '')
            if date_str:
                try:
                    date_obj = datetime.strptime(date_str, '%d.%m.%Y')
                    dates.append(date_obj)
                    
                    # Считаем программы
                    programs = day.get('data', [])
                    total_programs += len(programs)
                except ValueError:
                    continue
        
        if not dates:
            return {
                'start': None,
                'end': None,
                'days_count': 0,
                'programs_count': 0
            }
        
        dates.sort()
        return {
            'start': dates[0].isoformat(),
            'end': dates[-1].isoformat(),
            'days_count': len(dates),
            'programs_count': total_programs
        }
    
    def save_metadata(self, epg_data: List[Dict], request_params: Dict[str, str]):
        """Сохраняет метаданные."""
        coverage = self.analyze_data_coverage(epg_data)
        
        metadata = {
            'last_update': datetime.now().isoformat(),
            'request_params': request_params,
            'date_coverage': coverage,
            'version': '1.0'
        }
        
        self.data_dir.mkdir(exist_ok=True)
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Метаданные сохранены: {coverage['days_count']} дней, "
                   f"{coverage['programs_count']} программ")


def smart_fetch_epg_simple(cfg: Config, session, data_dir: str = "data") -> List[Dict[str, Any]]:
    """
    Упрощенная умная загрузка EPG данных.
    
    Args:
        cfg: Конфигурация
        session: HTTP сессия
        data_dir: Директория для данных
        
    Returns:
        Список EPG данных
    """
    logger.info("🧠 Запуск упрощенной умной загрузки EPG")
    
    manager = SimpleEPGManager(data_dir)
    
    # Проверяем нужно ли обновление
    should_update, reason = manager.should_update_epg()
    logger.info(f"📋 Проверка обновления: {reason}")
    
    # Загружаем существующие данные
    existing_data = []
    if manager.raw_epg_file.exists():
        try:
            with open(manager.raw_epg_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except Exception as e:
            logger.warning(f"Ошибка загрузки существующих данных: {e}")
            existing_data = []
    
    if not should_update:
        logger.info("✅ Данные актуальны, загрузка не требуется")
        return existing_data
    
    # Получаем оптимальные параметры запроса
    request_params = manager.get_optimal_request_params()
    logger.info(f"📡 Параметры запроса: epg_from={request_params['epg_from']}, "
               f"epg_limit={request_params['epg_limit']}")
    
    # Создаем временную конфигурацию
    temp_params = cfg.iptv_params.copy()
    temp_params.update(request_params)
    
    temp_cfg = Config(
        iptv_base_url=cfg.iptv_base_url,
        iptv_params=temp_params,
        iptv_headers=cfg.iptv_headers,
        http_timeout=cfg.http_timeout,
        http_retries=cfg.http_retries,
        http_backoff=cfg.http_backoff,
        cache_enabled=cfg.cache_enabled,
        cache_path=cfg.cache_path,
        cache_expire=cfg.cache_expire,
        tmdb_api_key=cfg.tmdb_api_key,
        tmdb_base_url=cfg.tmdb_base_url,
        tmdb_image_base=cfg.tmdb_image_base,
        log_level=cfg.log_level,
        api_host=cfg.api_host,
        api_port=cfg.api_port,
        api_cache_ttl=cfg.api_cache_ttl,
        api_cors_origins=cfg.api_cors_origins,
        auto_run_pipeline=cfg.auto_run_pipeline
    )
    
    # Выполняем запрос
    try:
        new_data = _original_fetch_epg(temp_cfg, session)
        logger.info(f"✅ Получено {len(new_data)} дней EPG данных")
    except Exception as e:
        logger.error(f"❌ Ошибка загрузки EPG: {e}")
        return existing_data
    
    # Объединяем данные
    merged_data = manager.merge_epg_data(existing_data, new_data)
    
    # Сохраняем результат
    manager.data_dir.mkdir(exist_ok=True)
    with open(manager.raw_epg_file, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    # Сохраняем метаданные
    manager.save_metadata(merged_data, request_params)
    
    logger.info(f"💾 Сохранено {len(merged_data)} дней EPG данных")
    return merged_data


# Заменяем основную функцию
def fetch_epg_smart(cfg: Config, session) -> List[Dict[str, Any]]:
    """Обертка для обратной совместимости."""
    return smart_fetch_epg_simple(cfg, session)
