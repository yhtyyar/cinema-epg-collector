"""
Модуль для проверки актуальности EPG данных и постеров.
Реализует умную логику определения необходимости обновления данных.
"""
from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

# Пути к файлам данных
RAW_EPG_PATH = Path("data/raw_epg.json")
MOVIES_PATH = Path("data/movies.json") 
ENRICHED_MOVIES_PATH = Path("data/enriched_movies.json")
POSTERS_DIR = Path("data/posters")


def is_file_fresh(file_path: Path, max_age_hours: int = 24) -> bool:
    """
    Проверяет, является ли файл свежим (создан/изменен в течение max_age_hours).
    
    Args:
        file_path: Путь к файлу
        max_age_hours: Максимальный возраст файла в часах
        
    Returns:
        True если файл свежий, False если устарел или не существует
    """
    if not file_path.exists():
        logger.debug(f"File {file_path} does not exist")
        return False
        
    try:
        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
        age_threshold = datetime.now() - timedelta(hours=max_age_hours)
        
        is_fresh = file_mtime > age_threshold
        logger.debug(f"File {file_path}: mtime={file_mtime}, threshold={age_threshold}, fresh={is_fresh}")
        return is_fresh
        
    except Exception as e:
        logger.error(f"Error checking file {file_path}: {e}")
        return False


def count_posters() -> int:
    """
    Подсчитывает количество файлов постеров в директории.
    
    Returns:
        Количество файлов постеров
    """
    if not POSTERS_DIR.exists():
        return 0
        
    try:
        poster_files = [f for f in POSTERS_DIR.iterdir() 
                       if f.is_file() and f.suffix.lower() in {'.jpg', '.jpeg', '.png', '.webp'}]
        count = len(poster_files)
        logger.debug(f"Found {count} poster files in {POSTERS_DIR}")
        return count
    except Exception as e:
        logger.error(f"Error counting posters in {POSTERS_DIR}: {e}")
        return 0


def validate_data_freshness(max_age_hours: int = 24) -> Tuple[bool, str]:
    """
    Проверяет актуальность всех данных EPG и постеров.
    
    Args:
        max_age_hours: Максимальный возраст данных в часах
        
    Returns:
        Tuple[bool, str]: (нужно_ли_обновление, причина)
    """
    reasons = []
    
    # Проверяем основной файл с обогащенными данными
    if not is_file_fresh(ENRICHED_MOVIES_PATH, max_age_hours):
        if not ENRICHED_MOVIES_PATH.exists():
            reasons.append("enriched_movies.json не существует")
        else:
            reasons.append(f"enriched_movies.json устарел (старше {max_age_hours}ч)")
    
    # Проверяем наличие постеров
    poster_count = count_posters()
    if poster_count == 0:
        reasons.append("папка data/posters пуста")
    
    # Проверяем промежуточные файлы если основной файл свежий
    if not reasons:
        if not is_file_fresh(RAW_EPG_PATH, max_age_hours):
            reasons.append("raw_epg.json устарел или отсутствует")
        elif not is_file_fresh(MOVIES_PATH, max_age_hours):
            reasons.append("movies.json устарел или отсутствует")
    
    needs_update = bool(reasons)
    reason_text = "; ".join(reasons) if reasons else "данные актуальны"
    
    logger.info(f"Data validation: needs_update={needs_update}, reason={reason_text}")
    return needs_update, reason_text


def should_run_pipeline(force_run: bool = False, max_age_hours: int = 24, skip_if_exists: bool = False) -> Tuple[bool, str]:
    """
    Определяет, нужно ли запускать пайплайн сбора данных.
    
    Args:
        force_run: Принудительный запуск (например, AUTO_RUN_PIPELINE=true)
        max_age_hours: Максимальный возраст данных в часах
        skip_if_exists: Пропустить запуск если данные уже существуют (даже если они старые)
        
    Returns:
        Tuple[bool, str]: (нужно_запускать, причина)
    """
    # Если принудительный запуск, то запускаем в любом случае
    if force_run:
        return True, "принудительный запуск (AUTO_RUN_PIPELINE=true)"
    
    # Проверяем, существуют ли уже данные и нужно ли пропустить обогащение
    if skip_if_exists and ENRICHED_MOVIES_PATH.exists():
        # Дополнительно проверяем, что файл не пустой
        try:
            if ENRICHED_MOVIES_PATH.stat().st_size > 0:
                # Пытаемся загрузить данные, чтобы убедиться, что они корректны
                import json
                data = json.loads(ENRICHED_MOVIES_PATH.read_text(encoding="utf-8"))
                if isinstance(data, list) and len(data) > 0:
                    return False, "данные уже существуют, пропускаем обогащение (SKIP_ENRICHMENT_IF_EXISTS=true)"
        except Exception:
            # Если не удалось прочитать файл, продолжаем как обычно
            pass
    
    # Проверяем актуальность данных
    needs_update, reason = validate_data_freshness(max_age_hours)
    return needs_update, reason


def cleanup_old_artifacts() -> None:
    """
    Очищает старые артефакты перед запуском пайплайна.
    """
    logger.info("Очистка старых артефактов...")
    
    # Удаляем старые JSON файлы
    for json_file in [RAW_EPG_PATH, MOVIES_PATH, ENRICHED_MOVIES_PATH]:
        if json_file.exists():
            try:
                json_file.unlink()
                logger.debug(f"Удален {json_file}")
            except Exception as e:
                logger.error(f"Ошибка при удалении {json_file}: {e}")
    
    # Очищаем папку постеров
    if POSTERS_DIR.exists():
        try:
            for poster_file in POSTERS_DIR.iterdir():
                if poster_file.is_file():
                    poster_file.unlink()
                    logger.debug(f"Удален постер {poster_file}")
        except Exception as e:
            logger.error(f"Ошибка при очистке постеров: {e}")
    
    # Очищаем кэш
    cache_dir = Path("cache")
    if cache_dir.exists():
        try:
            for cache_file in cache_dir.rglob("*"):
                if cache_file.is_file():
                    cache_file.unlink()
                    logger.debug(f"Удален кэш файл {cache_file}")
        except Exception as e:
            logger.error(f"Ошибка при очистке кэша: {e}")
    
    logger.info("Очистка артефактов завершена")


def get_data_status() -> dict:
    """
    Возвращает подробную информацию о состоянии данных.
    
    Returns:
        dict: Статус всех компонентов данных
    """
    # Проверяем существование и свежесть файлов, обрабатываем исключения
    raw_epg_status = {
        "exists": RAW_EPG_PATH.exists(),
        "fresh": False,
        "mtime": None
    }
    if RAW_EPG_PATH.exists():
        try:
            raw_epg_status["fresh"] = is_file_fresh(RAW_EPG_PATH)
            raw_epg_status["mtime"] = datetime.fromtimestamp(RAW_EPG_PATH.stat().st_mtime).isoformat()
        except Exception as e:
            logger.error(f"Error getting raw EPG status: {e}")
    
    movies_status = {
        "exists": MOVIES_PATH.exists(),
        "fresh": False,
        "mtime": None
    }
    if MOVIES_PATH.exists():
        try:
            movies_status["fresh"] = is_file_fresh(MOVIES_PATH)
            movies_status["mtime"] = datetime.fromtimestamp(MOVIES_PATH.stat().st_mtime).isoformat()
        except Exception as e:
            logger.error(f"Error getting movies status: {e}")
    
    enriched_movies_status = {
        "exists": ENRICHED_MOVIES_PATH.exists(),
        "fresh": False,
        "mtime": None,
        "size": 0
    }
    if ENRICHED_MOVIES_PATH.exists():
        try:
            enriched_movies_status["fresh"] = is_file_fresh(ENRICHED_MOVIES_PATH)
            enriched_movies_status["mtime"] = datetime.fromtimestamp(ENRICHED_MOVIES_PATH.stat().st_mtime).isoformat()
            enriched_movies_status["size"] = ENRICHED_MOVIES_PATH.stat().st_size
        except Exception as e:
            logger.error(f"Error getting enriched movies status: {e}")
    
    return {
        "raw_epg": raw_epg_status,
        "movies": movies_status,
        "enriched_movies": enriched_movies_status,
        "posters": {
            "directory_exists": POSTERS_DIR.exists(),
            "count": count_posters(),
            "fresh": count_posters() > 0
        }
    }