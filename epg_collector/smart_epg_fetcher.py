"""
Smart EPG Fetcher - Интеллектуальная система загрузки EPG с инкрементальным обновлением.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

from .config import Config
from .epg_manager import EPGManager
from .iptv_api import fetch_epg as _original_fetch_epg

logger = logging.getLogger(__name__)


def smart_fetch_epg(cfg: Config, session, data_dir: str = "data") -> List[Dict[str, Any]]:
    """
    Умная загрузка EPG данных с инкрементальным обновлением.
    
    Логика работы:
    1. Анализирует существующие данные
    2. Определяет недостающие временные диапазоны
    3. Загружает только необходимые данные
    4. Объединяет с существующими данными
    5. Очищает устаревшие записи
    
    Args:
        cfg: Конфигурация
        session: HTTP сессия
        data_dir: Директория для данных
        
    Returns:
        Полный список EPG данных
    """
    logger.info("🧠 Запуск умной загрузки EPG данных")
    
    # Инициализируем менеджер EPG
    epg_manager = EPGManager(data_dir)
    
    # Определяем целевой диапазон дат
    target_range = epg_manager.get_target_date_range()
    logger.info(f"🎯 Целевой диапазон: {target_range.start.date()} - {target_range.end.date()}")
    
    # Анализируем существующие данные
    analysis = epg_manager.analyze_existing_data(target_range)
    
    if not analysis.needs_update:
        logger.info("✅ Данные актуальны, загрузка не требуется")
        # Загружаем существующие данные
        raw_epg_file = Path(data_dir) / "raw_epg.json"
        if raw_epg_file.exists():
            with open(raw_epg_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    logger.info(f"📊 Анализ: {len(analysis.existing_ranges)} существующих диапазонов, "
               f"{len(analysis.missing_ranges)} недостающих")
    
    # Загружаем существующие данные
    existing_data = []
    raw_epg_file = Path(data_dir) / "raw_epg.json"
    if raw_epg_file.exists():
        try:
            with open(raw_epg_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            logger.warning("Ошибка загрузки существующих данных, начинаем с пустого списка")
            existing_data = []
    
    # Если есть недостающие диапазоны, загружаем их
    all_new_data = []
    if analysis.missing_ranges:
        request_params_list = epg_manager.calculate_optimal_request_params(analysis.missing_ranges)
        
        for i, request_params in enumerate(request_params_list, 1):
            logger.info(f"📡 Запрос {i}/{len(request_params_list)}: {request_params['range_description']}")
            
            # Создаем временную конфигурацию с новыми параметрами
            temp_cfg = _create_temp_config(cfg, request_params)
            
            # Выполняем запрос
            try:
                new_data = _original_fetch_epg(temp_cfg, session)
                all_new_data.extend(new_data)
                logger.info(f"✅ Получено {len(new_data)} элементов для диапазона")
            except Exception as e:
                logger.error(f"❌ Ошибка загрузки диапазона {request_params['range_description']}: {e}")
                continue
    
    # Объединяем данные
    if all_new_data or analysis.outdated_items:
        logger.info(f"🔄 Объединение данных: {len(existing_data)} + {len(all_new_data)} новых")
        merged_data = epg_manager.merge_epg_data(existing_data, all_new_data)
        
        # Сохраняем объединенные данные
        raw_epg_file.parent.mkdir(exist_ok=True)
        with open(raw_epg_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        
        # Сохраняем метаданные
        epg_manager.save_metadata(analysis, request_params_list if analysis.missing_ranges else [])
        
        logger.info(f"💾 Сохранено {len(merged_data)} элементов EPG")
        return merged_data
    else:
        logger.info("ℹ️ Новых данных для загрузки нет")
        return existing_data


def _create_temp_config(original_cfg: Config, request_params: Dict[str, str]) -> Config:
    """Создает временную конфигурацию с новыми параметрами запроса."""
    # Копируем оригинальные параметры
    temp_params = original_cfg.iptv_params.copy()
    
    # Обновляем параметры времени
    temp_params.update({
        "epg_from": request_params["epg_from"],
        "epg_limit": request_params["epg_limit"]
    })
    
    # Создаем новую конфигурацию
    temp_cfg = Config(
        iptv_base_url=original_cfg.iptv_base_url,
        iptv_params=temp_params,
        iptv_headers=original_cfg.iptv_headers,
        http_timeout=original_cfg.http_timeout,
        http_retries=original_cfg.http_retries,
        http_backoff=original_cfg.http_backoff,
        cache_enabled=original_cfg.cache_enabled,
        cache_path=original_cfg.cache_path,
        cache_expire=original_cfg.cache_expire,
        tmdb_api_key=original_cfg.tmdb_api_key,
        tmdb_base_url=original_cfg.tmdb_base_url,
        tmdb_image_base=original_cfg.tmdb_image_base,
        log_level=original_cfg.log_level,
        api_host=original_cfg.api_host,
        api_port=original_cfg.api_port,
        api_cache_ttl=original_cfg.api_cache_ttl,
        api_cors_origins=original_cfg.api_cors_origins,
        auto_run_pipeline=original_cfg.auto_run_pipeline
    )
    
    return temp_cfg


# Обратная совместимость - заменяем оригинальную функцию
def fetch_epg(cfg: Config, session) -> List[Dict[str, Any]]:
    """Обертка для обратной совместимости."""
    return smart_fetch_epg(cfg, session)
