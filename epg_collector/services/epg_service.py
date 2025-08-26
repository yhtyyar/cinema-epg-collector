"""Сервис для работы с EPG данными."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..config import Config
from ..iptv_api import fetch_epg, fetch_epg_for_channel
from ..filters import filter_movies_by_category, filter_cartoons_by_category

logger = logging.getLogger(__name__)


class EPGService:
    """Сервис для работы с EPG данными."""
    
    def __init__(self, config: Config, session, data_dir: Path):
        self.config = config
        self.session = session
        self.data_dir = data_dir
        
    def fetch_and_save_epg(self) -> List[Dict[str, Any]]:
        """Загружает EPG и сохраняет в файл."""
        logger.info("Начинаем загрузку EPG данных")
        
        epg_data = fetch_epg(self.config, self.session)
        
        raw_path = self.data_dir / "raw_epg.json"
        raw_path.write_text(
            json.dumps(epg_data, ensure_ascii=False, indent=2), 
            encoding="utf-8"
        )
        
        logger.info(f"Сохранено {len(epg_data)} элементов EPG в {raw_path}")
        return epg_data
        
    def filter_movies_from_epg(self, epg_data: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Фильтрует фильмы из EPG данных."""
        if epg_data is None:
            raw_path = self.data_dir / "raw_epg.json"
            if not raw_path.exists():
                raise FileNotFoundError(f"EPG файл не найден: {raw_path}")
            epg_data = json.loads(raw_path.read_text(encoding="utf-8"))
            
        logger.info("Начинаем фильтрацию фильмов")
        
        # Обработка разных форматов данных
        items: List[Dict[str, Any]] = []
        for elem in epg_data:
            if isinstance(elem, dict) and isinstance(elem.get("data"), list):
                items.extend(elem["data"])
            elif isinstance(elem, dict):
                items.append(elem)
                
        movies = filter_movies_by_category(items)
        
        movies_path = self.data_dir / "movies.json"
        movies_path.write_text(
            json.dumps(movies, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        logger.info(f"Отфильтровано {len(movies)} фильмов, сохранено в {movies_path}")
        return movies
        
    def process_channel_epg(self, channel_ids: List[str], limit: Optional[int] = None) -> int:
        """Обрабатывает EPG для списка каналов."""
        if limit:
            channel_ids = channel_ids[:limit]
            
        epg_channels_dir = self.data_dir / "epg_channels"
        epg_channels_dir.mkdir(parents=True, exist_ok=True)
        
        saved_count = 0
        
        for channel_id in channel_ids:
            try:
                logger.debug(f"Обрабатываем канал {channel_id}")
                
                epg_items = fetch_epg_for_channel(self.config, self.session, channel_id)
                channel_data = {"our_id": channel_id, "epg": epg_items}
                
                output_path = epg_channels_dir / f"{channel_id}.json"
                output_path.write_text(
                    json.dumps(channel_data, ensure_ascii=False, indent=2),
                    encoding="utf-8"
                )
                saved_count += 1
                
            except Exception as e:
                logger.error(f"Ошибка обработки канала {channel_id}: {e}")
                continue
                
        logger.info(f"Обработано {saved_count} каналов")
        return saved_count
