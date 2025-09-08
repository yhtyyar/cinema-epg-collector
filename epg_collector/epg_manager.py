"""
EPG Manager - Умное управление EPG данными с инкрементальным обновлением.

Основные функции:
- Анализ существующих данных по временным диапазонам
- Определение недостающих периодов
- Инкрементальное обновление только новых данных
- Очистка устаревших записей
- Объединение и дедупликация данных
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DateRange:
    """Представляет временной диапазон."""
    start: datetime
    end: datetime
    
    def overlaps(self, other: 'DateRange') -> bool:
        """Проверяет пересечение с другим диапазоном."""
        return self.start <= other.end and self.end >= other.start
    
    def contains(self, date: datetime) -> bool:
        """Проверяет, содержится ли дата в диапазоне."""
        return self.start <= date <= self.end
    
    def days_count(self) -> int:
        """Возвращает количество дней в диапазоне."""
        return (self.end - self.start).days + 1


@dataclass
class EPGAnalysis:
    """Результат анализа существующих EPG данных."""
    existing_ranges: List[DateRange]
    missing_ranges: List[DateRange]
    outdated_items: List[Dict[str, Any]]
    total_items: int
    date_coverage: DateRange
    needs_update: bool


class EPGManager:
    """Менеджер для умного управления EPG данными."""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.raw_epg_file = self.data_dir / "raw_epg.json"
        self.epg_metadata_file = self.data_dir / "epg_metadata.json"
        
        # Настройки временных диапазонов
        self.default_past_days = 7
        self.default_future_days = 14
        self.cleanup_threshold_days = 30  # Удаляем данные старше 30 дней
        
    def analyze_existing_data(self, target_range: DateRange) -> EPGAnalysis:
        """
        Анализирует существующие EPG данные и определяет что нужно обновить.
        
        Args:
            target_range: Желаемый временной диапазон
            
        Returns:
            EPGAnalysis с информацией о покрытии и недостающих данных
        """
        logger.info(f"Анализ существующих EPG данных для диапазона {target_range.start} - {target_range.end}")
        
        if not self.raw_epg_file.exists():
            logger.info("Файл raw_epg.json не существует, требуется полная загрузка")
            return EPGAnalysis(
                existing_ranges=[],
                missing_ranges=[target_range],
                outdated_items=[],
                total_items=0,
                date_coverage=target_range,
                needs_update=True
            )
        
        # Загружаем существующие данные
        try:
            with open(self.raw_epg_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logger.warning(f"Ошибка чтения существующих данных: {e}")
            return EPGAnalysis(
                existing_ranges=[],
                missing_ranges=[target_range],
                outdated_items=[],
                total_items=0,
                date_coverage=target_range,
                needs_update=True
            )
        
        if not existing_data:
            logger.info("Существующие данные пусты")
            return EPGAnalysis(
                existing_ranges=[],
                missing_ranges=[target_range],
                outdated_items=[],
                total_items=0,
                date_coverage=target_range,
                needs_update=True
            )
        
        # Анализируем временное покрытие существующих данных
        existing_dates = set()
        outdated_items = []
        cutoff_date = datetime.now() - timedelta(days=self.cleanup_threshold_days)
        
        for item in existing_data:
            try:
                # Обрабатываем вложенную структуру EPG
                if 'data' in item and isinstance(item['data'], list):
                    # Это элемент с вложенными программами
                    for program in item['data']:
                        date_str = self._extract_date_from_program(program)
                        if date_str:
                            item_date = self._parse_date(date_str)
                            if item_date:
                                date_only = item_date.date()
                                existing_dates.add(date_only)
                                if item_date < cutoff_date:
                                    outdated_items.append(program)
                else:
                    # Это отдельная программа
                    date_str = self._extract_date_from_program(item)
                    if date_str:
                        item_date = self._parse_date(date_str)
                        if item_date:
                            date_only = item_date.date()
                            existing_dates.add(date_only)
                            if item_date < cutoff_date:
                                outdated_items.append(item)
                    
            except Exception as e:
                logger.warning(f"Ошибка обработки элемента EPG: {e}")
                continue
        
        if not existing_dates:
            logger.info("Не найдено валидных дат в существующих данных")
            return EPGAnalysis(
                existing_ranges=[],
                missing_ranges=[target_range],
                outdated_items=outdated_items,
                total_items=len(existing_data),
                date_coverage=target_range,
                needs_update=True
            )
        
        # Определяем существующие диапазоны
        sorted_dates = sorted(existing_dates)
        existing_ranges = self._build_date_ranges(sorted_dates)
        
        # Определяем недостающие диапазоны
        missing_ranges = self._find_missing_ranges(target_range, existing_ranges)
        
        # Определяем общее покрытие
        min_date = datetime.combine(min(existing_dates), datetime.min.time())
        max_date = datetime.combine(max(existing_dates), datetime.max.time())
        date_coverage = DateRange(min_date, max_date)
        
        needs_update = len(missing_ranges) > 0 or len(outdated_items) > 0
        
        logger.info(f"Анализ завершен: {len(existing_ranges)} существующих диапазонов, "
                   f"{len(missing_ranges)} недостающих, {len(outdated_items)} устаревших")
        
        return EPGAnalysis(
            existing_ranges=existing_ranges,
            missing_ranges=missing_ranges,
            outdated_items=outdated_items,
            total_items=len(existing_data),
            date_coverage=date_coverage,
            needs_update=needs_update
        )
    
    def _build_date_ranges(self, sorted_dates: List) -> List[DateRange]:
        """Строит непрерывные диапазоны из отсортированного списка дат."""
        if not sorted_dates:
            return []
        
        ranges = []
        start_date = sorted_dates[0]
        end_date = sorted_dates[0]
        
        for date in sorted_dates[1:]:
            if (date - end_date).days <= 1:  # Непрерывность или соседние дни
                end_date = date
            else:
                # Завершаем текущий диапазон
                ranges.append(DateRange(
                    datetime.combine(start_date, datetime.min.time()),
                    datetime.combine(end_date, datetime.max.time())
                ))
                start_date = date
                end_date = date
        
        # Добавляем последний диапазон
        ranges.append(DateRange(
            datetime.combine(start_date, datetime.min.time()),
            datetime.combine(end_date, datetime.max.time())
        ))
        
        return ranges
    
    def _find_missing_ranges(self, target: DateRange, existing: List[DateRange]) -> List[DateRange]:
        """Находит недостающие диапазоны в целевом диапазоне."""
        if not existing:
            return [target]
        
        missing = []
        current_start = target.start
        
        for existing_range in sorted(existing, key=lambda r: r.start):
            # Если есть пропуск перед текущим существующим диапазоном
            if current_start < existing_range.start:
                gap_end = min(existing_range.start - timedelta(seconds=1), target.end)
                if current_start <= gap_end:
                    missing.append(DateRange(current_start, gap_end))
            
            # Обновляем текущую позицию
            current_start = max(current_start, existing_range.end + timedelta(seconds=1))
            
            # Если мы уже покрыли весь целевой диапазон
            if current_start > target.end:
                break
        
        # Проверяем, есть ли пропуск в конце
        if current_start <= target.end:
            missing.append(DateRange(current_start, target.end))
        
        return missing
    
    def calculate_optimal_request_params(self, missing_ranges: List[DateRange]) -> List[Dict[str, str]]:
        """
        Вычисляет оптимальные параметры для API запросов на основе недостающих диапазонов.
        
        Returns:
            Список параметров для множественных запросов если необходимо
        """
        if not missing_ranges:
            return []
        
        requests = []
        today = datetime.now().date()
        
        for range_item in missing_ranges:
            # Вычисляем параметры относительно сегодняшнего дня
            start_date = range_item.start.date()
            end_date = range_item.end.date()
            
            days_from_today_start = (start_date - today).days
            days_from_today_end = (end_date - today).days
            
            # Формируем параметры запроса
            epg_from = str(days_from_today_start)
            epg_limit = str(days_from_today_end - days_from_today_start + 1)
            
            requests.append({
                "epg_from": epg_from,
                "epg_limit": epg_limit,
                "range_description": f"{start_date} to {end_date} ({epg_limit} days)"
            })
            
            logger.info(f"Запрос для диапазона {start_date} - {end_date}: "
                       f"epg_from={epg_from}, epg_limit={epg_limit}")
        
        return requests
    
    def merge_epg_data(self, existing_data: List[Dict], new_data: List[Dict]) -> List[Dict]:
        """
        Объединяет существующие и новые EPG данные с дедупликацией.
        
        Args:
            existing_data: Существующие данные
            new_data: Новые данные для добавления
            
        Returns:
            Объединенный и дедуплицированный список
        """
        logger.info(f"Объединение данных: {len(existing_data)} существующих + {len(new_data)} новых")
        
        # Нормализуем данные к плоской структуре программ
        existing_programs = self._flatten_epg_data(existing_data)
        new_programs = self._flatten_epg_data(new_data)
        
        logger.info(f"После нормализации: {len(existing_programs)} существующих программ + {len(new_programs)} новых")
        
        # Создаем индекс существующих программ для быстрого поиска
        existing_index = {}
        for program in existing_programs:
            key = self._create_item_key(program)
            if key:
                existing_index[key] = program
        
        # Добавляем новые программы, избегая дубликатов
        added_count = 0
        updated_count = 0
        
        for new_program in new_programs:
            key = self._create_item_key(new_program)
            if not key:
                continue
                
            if key in existing_index:
                # Обновляем существующую программу если новая содержит больше данных
                if self._should_update_item(existing_index[key], new_program):
                    existing_index[key] = new_program
                    updated_count += 1
            else:
                # Добавляем новую программу
                existing_index[key] = new_program
                added_count += 1
        
        # Фильтруем устаревшие данные
        cutoff_date = datetime.now() - timedelta(days=self.cleanup_threshold_days)
        filtered_programs = []
        removed_count = 0
        
        for program in existing_index.values():
            try:
                date_str = self._extract_date_from_program(program)
                if date_str:
                    program_date = self._parse_date(date_str)
                    if program_date and program_date >= cutoff_date:
                        filtered_programs.append(program)
                    elif program_date and program_date < cutoff_date:
                        removed_count += 1
                    else:
                        # Если не удалось распарсить дату, сохраняем программу
                        filtered_programs.append(program)
                else:
                    # Если нет даты, сохраняем программу
                    filtered_programs.append(program)
            except Exception as e:
                logger.warning(f"Ошибка фильтрации программы: {e}")
                filtered_programs.append(program)  # Сохраняем при ошибке
        
        # Группируем программы обратно по дням для сохранения в оригинальном формате
        grouped_data = self._group_programs_by_date(filtered_programs)
        
        logger.info(f"Объединение завершено: добавлено {added_count}, обновлено {updated_count}, "
                   f"удалено устаревших {removed_count}, итого {len(grouped_data)} дней с программами")
        
        return grouped_data
    
    def _flatten_epg_data(self, epg_data: List[Dict]) -> List[Dict]:
        """Преобразует вложенную структуру EPG в плоский список программ."""
        programs = []
        
        for item in epg_data:
            if 'data' in item and isinstance(item['data'], list):
                # Это элемент с вложенными программами
                for program in item['data']:
                    # Добавляем информацию о дне к программе
                    program_copy = program.copy()
                    program_copy['_epg_date'] = item.get('date', '')
                    program_copy['_epg_title'] = item.get('title', '')
                    programs.append(program_copy)
            else:
                # Это отдельная программа
                programs.append(item)
        
        return programs
    
    def _group_programs_by_date(self, programs: List[Dict]) -> List[Dict]:
        """Группирует программы обратно по дням."""
        from collections import defaultdict
        
        grouped = defaultdict(list)
        
        for program in programs:
            # Определяем дату программы
            date_str = self._extract_date_from_program(program)
            if date_str:
                program_date = self._parse_date(date_str)
                if program_date:
                    date_key = program_date.strftime('%d.%m.%Y')
                    
                    # Удаляем служебные поля
                    clean_program = {k: v for k, v in program.items() 
                                   if not k.startswith('_epg_')}
                    grouped[date_key].append(clean_program)
        
        # Формируем результат в оригинальном формате
        result = []
        for date_key, day_programs in grouped.items():
            if day_programs:  # Только если есть программы
                try:
                    # Парсим дату для сортировки
                    date_obj = datetime.strptime(date_key, '%d.%m.%Y')
                    weekday_names = ['ПН', 'ВТ', 'СР', 'ЧТ', 'ПТ', 'СБ', 'ВС']
                    weekday = weekday_names[date_obj.weekday()]
                    
                    result.append({
                        'date': date_key,
                        'title': f"{date_key} {weekday}",
                        'data': sorted(day_programs, key=lambda x: x.get('timestart', 0)),
                        'current': False
                    })
                except ValueError:
                    # Если не удалось распарсить дату, используем как есть
                    result.append({
                        'date': date_key,
                        'title': date_key,
                        'data': day_programs,
                        'current': False
                    })
        
        # Сортируем по дате
        result.sort(key=lambda x: x['date'])
        
        return result
    
    def _create_item_key(self, item: Dict) -> Optional[str]:
        """Создает уникальный ключ для элемента EPG."""
        # Используем комбинацию полей для уникальной идентификации
        title = item.get('title', '').strip()
        start_time = (item.get('timestart') or 
                     item.get('broadcast_time') or 
                     item.get('start_time') or 
                     item.get('time_start', ''))
        
        # Пробуем разные поля для ID
        item_id = (item.get('id') or 
                  item.get('channel_id') or 
                  item.get('program_id') or 
                  item.get('epg_id', ''))
        
        if not title:
            return None
            
        # Если нет времени, используем только title + id
        if not start_time:
            return f"{title}|{item_id}" if item_id else f"{title}"
            
        return f"{title}|{start_time}|{item_id}"
    
    def _extract_date_from_program(self, program: Dict) -> Optional[str]:
        """Извлекает дату из программы EPG."""
        # Пробуем разные поля для времени
        date_fields = [
            'mskdatetimestart', 'usrdatetimestart', 'timestart', 
            'broadcast_time', 'start_time', 'time_start'
        ]
        
        for field in date_fields:
            value = program.get(field)
            if value:
                # Если это timestamp (число)
                if isinstance(value, (int, float)):
                    try:
                        return datetime.fromtimestamp(value).isoformat()
                    except (ValueError, OSError):
                        continue
                # Если это строка
                elif isinstance(value, str):
                    return value
        
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Парсит дату из строки в различных форматах."""
        if not date_str:
            return None
            
        try:
            # Обрабатываем различные форматы дат
            if 'T' in date_str:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                # Попробуем другие форматы
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d.%m.%Y %H:%M', '%d.%m.%Y']:
                    try:
                        return datetime.strptime(date_str, fmt)
                    except ValueError:
                        continue
                        
                # Если это timestamp в виде строки
                try:
                    timestamp = float(date_str)
                    return datetime.fromtimestamp(timestamp)
                except (ValueError, OSError):
                    pass
                    
        except Exception as e:
            logger.warning(f"Ошибка парсинга даты '{date_str}': {e}")
            
        return None
    
    def _should_update_item(self, existing: Dict, new: Dict) -> bool:
        """Определяет, следует ли обновить существующий элемент новым."""
        # Обновляем если новый элемент содержит больше полей
        existing_fields = len([v for v in existing.values() if v])
        new_fields = len([v for v in new.values() if v])
        
        return new_fields > existing_fields
    
    def save_metadata(self, analysis: EPGAnalysis, request_params: List[Dict]):
        """Сохраняет метаданные о последнем обновлении EPG."""
        metadata = {
            "last_update": datetime.now().isoformat(),
            "total_items": analysis.total_items,
            "date_coverage": {
                "start": analysis.date_coverage.start.isoformat(),
                "end": analysis.date_coverage.end.isoformat()
            },
            "existing_ranges": [
                {
                    "start": r.start.isoformat(),
                    "end": r.end.isoformat(),
                    "days": r.days_count()
                }
                for r in analysis.existing_ranges
            ],
            "last_requests": request_params,
            "cleanup_threshold_days": self.cleanup_threshold_days
        }
        
        self.data_dir.mkdir(exist_ok=True)
        with open(self.epg_metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Метаданные EPG сохранены в {self.epg_metadata_file}")
    
    def get_target_date_range(self, past_days: Optional[int] = None, 
                             future_days: Optional[int] = None) -> DateRange:
        """Возвращает целевой диапазон дат для EPG данных."""
        past_days = past_days or self.default_past_days
        future_days = future_days or self.default_future_days
        
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        start_date = today - timedelta(days=past_days)
        end_date = today + timedelta(days=future_days)
        
        return DateRange(start_date, end_date)
