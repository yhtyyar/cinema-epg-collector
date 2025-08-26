"""Сервис для обогащения данных фильмов."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..config import Config
from ..kinopoisk import KinoPoiskClient
from ..tmdb import TMDBClient
from ..posters import download_poster

logger = logging.getLogger(__name__)


class EnrichmentService:
    """Сервис для обогащения данных о фильмах."""
    
    def __init__(self, config: Config, session, data_dir: Path):
        self.config = config
        self.session = session
        self.data_dir = data_dir
        self.kinopoisk_client = KinoPoiskClient(config, session)
        self.tmdb_client = TMDBClient(config, session) if config.tmdb_api_key else None
        
    def enrich_movies(self, movies: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """Обогащает фильмы данными из КиноПоиска и TMDB."""
        if movies is None:
            movies_path = self.data_dir / "movies.json"
            if not movies_path.exists():
                raise FileNotFoundError(f"Файл фильмов не найден: {movies_path}")
            movies = json.loads(movies_path.read_text(encoding="utf-8"))
            
        logger.info(f"Начинаем обогащение {len(movies)} фильмов")
        
        enriched_movies = []
        posters_dir = self.data_dir / "posters"
        posters_dir.mkdir(parents=True, exist_ok=True)
        
        for movie in movies:
            try:
                enriched_movie = self._enrich_single_movie(movie, posters_dir)
                enriched_movies.append(enriched_movie)
            except Exception as e:
                logger.error(f"Ошибка обогащения фильма {movie.get('title', 'Unknown')}: {e}")
                enriched_movies.append(movie)  # Сохраняем оригинал при ошибке
                
        # Сохраняем результат
        enriched_path = self.data_dir / "enriched_movies.json"
        enriched_path.write_text(
            json.dumps(enriched_movies, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        logger.info(f"Обогащение завершено, сохранено в {enriched_path}")
        return enriched_movies
        
    def _enrich_single_movie(self, movie: Dict[str, Any], posters_dir: Path) -> Dict[str, Any]:
        """Обогащает один фильм."""
        title = movie.get("title", "")
        if not title:
            return movie
            
        enriched = dict(movie)
        
        # Получаем данные из КиноПоиска
        kinopoisk_data = self.kinopoisk_client.get_movie_info(title)
        if kinopoisk_data:
            enriched["kinopoisk"] = kinopoisk_data
            
        # Получаем данные из TMDB (если доступен)
        if self.tmdb_client:
            tmdb_data = self.tmdb_client.get_movie_info(title)
            if tmdb_data:
                enriched["tmdb"] = tmdb_data
                
        # Скачиваем постер
        poster_info = self._download_movie_poster(enriched, posters_dir)
        if poster_info:
            enriched.update(poster_info)
            
        return enriched
        
    def _download_movie_poster(self, movie: Dict[str, Any], posters_dir: Path) -> Optional[Dict[str, Any]]:
        """Скачивает постер для фильма."""
        title = movie.get("title", "")
        movie_id = movie.get("id", "unknown")
        
        # Приоритет источников постеров: TMDB -> КиноПоиск -> EPG preview
        poster_candidates = []
        
        # TMDB постер
        if self.tmdb_client and movie.get("tmdb", {}).get("poster_url"):
            poster_candidates.append({
                "url": movie["tmdb"]["poster_url"],
                "source": "tmdb"
            })
            
        # КиноПоиск постер
        if movie.get("kinopoisk", {}).get("poster_url"):
            poster_candidates.append({
                "url": movie["kinopoisk"]["poster_url"],
                "source": "kinopoisk"
            })
            
        # EPG preview
        if movie.get("preview"):
            poster_candidates.append({
                "url": movie["preview"],
                "source": "preview"
            })
            
        # Пытаемся скачать постер
        for candidate in poster_candidates:
            try:
                local_path = download_poster(
                    session=self.session,
                    url=candidate["url"],
                    posters_dir=posters_dir,
                    title=title,
                    epg_id=movie_id,
                    source=candidate["source"]
                )
                
                if local_path:
                    return {
                        "poster_local": local_path,
                        "poster_source": candidate["source"]
                    }
                    
            except Exception as e:
                logger.debug(f"Не удалось скачать постер из {candidate['source']}: {e}")
                continue
                
        return None
        
    def enrich_movies_parallel(self, movies: Optional[List[Dict[str, Any]]] = None, max_workers: int = 4) -> List[Dict[str, Any]]:
        """Параллельное обогащение фильмов."""
        if movies is None:
            movies_path = self.data_dir / "movies.json"
            if not movies_path.exists():
                raise FileNotFoundError(f"Файл фильмов не найден: {movies_path}")
            movies = json.loads(movies_path.read_text(encoding="utf-8"))
            
        logger.info(f"Начинаем параллельное обогащение {len(movies)} фильмов ({max_workers} потоков)")
        
        posters_dir = self.data_dir / "posters"
        posters_dir.mkdir(parents=True, exist_ok=True)
        
        enriched_movies = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Создаем задачи
            future_to_movie = {
                executor.submit(self._enrich_single_movie, movie, posters_dir): movie 
                for movie in movies
            }
            
            # Собираем результаты
            for future in as_completed(future_to_movie):
                original_movie = future_to_movie[future]
                try:
                    enriched_movie = future.result()
                    enriched_movies.append(enriched_movie)
                except Exception as e:
                    logger.error(f"Ошибка обогащения фильма {original_movie.get('title', 'Unknown')}: {e}")
                    enriched_movies.append(original_movie)
                    
        # Сохраняем результат
        enriched_path = self.data_dir / "enriched_movies.json"
        enriched_path.write_text(
            json.dumps(enriched_movies, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        
        logger.info(f"Параллельное обогащение завершено, сохранено в {enriched_path}")
        return enriched_movies
