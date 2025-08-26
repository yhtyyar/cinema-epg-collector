from __future__ import annotations

import math
from typing import Optional, List
from pathlib import Path
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse

from epg_collector.api.models import (
    MoviesResponse,
    Pagination,
    Movie,
    ChannelsResponse,
    ChannelItem,
    ChannelData,
)
from epg_collector.api.dependencies import get_repository, get_cache, get_settings
from epg_collector.api.repository import MoviesRepository
from epg_collector.api.cache import TTLCache
from epg_collector.config import Config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["api"])


def _cache_key(path: str, **params) -> str:
    items = ",".join(f"{k}={v}" for k, v in sorted(params.items()))
    return f"{path}?{items}"


@router.get("/movies", response_model=MoviesResponse)
async def list_movies(
    page: int = Query(1, ge=1, description="Страница"),
    per_page: int = Query(50, ge=1, le=200, description="Размер страницы"),
    genre: Optional[str] = Query(None, description="Фильтр по жанру"),
    year: Optional[int] = Query(None, description="Фильтр по году"),
    rating_gte: Optional[float] = Query(None, ge=0.0, le=10.0, description="Минимальный рейтинг"),
    source: Optional[str] = Query(None, description="Источник постера: kinopoisk|tmdb|preview|null"),
    q: Optional[str] = Query(None, description="Поиск по названию"),
    repo: MoviesRepository = Depends(get_repository),
    cache: TTLCache = Depends(get_cache),
) -> MoviesResponse:
    key = _cache_key(
        "/api/movies",
        page=page,
        per_page=per_page,
        genre=genre or "",
        year=year or "",
        rating_gte=rating_gte or "",
        source=source or "",
        q=q or "",
    )
    cached = cache.get(key)
    if cached is not None:
        return cached

    items, total = repo.list_movies(
        page=page,
        per_page=per_page,
        genre=genre,
        year=year,
        rating_gte=rating_gte,
        source=source,
        search_q=q,
    )
    pages = math.ceil(total / per_page) if per_page else 1
    resp = MoviesResponse(
        movies=items,
        pagination=Pagination(page=page, per_page=per_page, total=total, pages=pages),
    )
    cache.set(key, resp)
    return resp


@router.get("/movies/search", response_model=MoviesResponse)
async def search_movies(
    q: str = Query(..., min_length=1, description="Строка поиска"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    repo: MoviesRepository = Depends(get_repository),
    cache: TTLCache = Depends(get_cache),
) -> MoviesResponse:
    key = _cache_key("/api/movies/search", q=q, page=page, per_page=per_page)
    cached = cache.get(key)
    if cached is not None:
        return cached

    items, total = repo.list_movies(page=page, per_page=per_page, search_q=q)
    pages = math.ceil(total / per_page) if per_page else 1
    resp = MoviesResponse(
        movies=items,
        pagination=Pagination(page=page, per_page=per_page, total=total, pages=pages),
    )
    cache.set(key, resp)
    return resp


@router.get("/movies/{movie_id}", response_model=Movie)
async def get_movie(
    movie_id: str,
    repo: MoviesRepository = Depends(get_repository),
) -> Movie:
    movie = repo.get_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


# --- Data directories ---

MOVIES_DIR = Path("data")
CHANNEL_MOVIES_DIR = Path("data/channel_json/movies")
CHANNEL_CARTOONS_DIR = Path("data/channel_json/cartoons")


def _list_channels_from_dir(directory: Path) -> List[ChannelItem]:
    channels: List[ChannelItem] = []
    if not directory.exists():
        return channels
    
    for p in sorted(directory.glob("*.json")):
        try:
            # Читаем файл с правильной кодировкой
            content = p.read_text(encoding="utf-8")
            obj = json.loads(content)
            
            # Безопасное извлечение данных
            cid = str(obj.get("our_id") or p.stem)
            items = obj.get("items", [])
            cnt = int(obj.get("count") or (len(items) if isinstance(items, list) else 0))
            
            channels.append(ChannelItem(id=cid, count=cnt))
            
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.warning(f"Failed to parse channel file {p}: {e}")
            continue
        except Exception as e:
            logger.error(f"Unexpected error reading channel file {p}: {e}")
            continue
            
    return channels


@router.get("/channels/movies", response_model=ChannelsResponse)
async def list_channels_movies(cache: TTLCache = Depends(get_cache)) -> ChannelsResponse:
    key = _cache_key("/api/channels/movies")
    cached = cache.get(key)
    if cached is not None:
        return cached
    channels = _list_channels_from_dir(CHANNEL_MOVIES_DIR)
    resp = ChannelsResponse(channels=channels)
    cache.set(key, resp)
    return resp


@router.get("/channels/cartoons", response_model=ChannelsResponse)
async def list_channels_cartoons(cache: TTLCache = Depends(get_cache)) -> ChannelsResponse:
    key = _cache_key("/api/channels/cartoons")
    cached = cache.get(key)
    if cached is not None:
        return cached
    channels = _list_channels_from_dir(CHANNEL_CARTOONS_DIR)
    resp = ChannelsResponse(channels=channels)
    cache.set(key, resp)
    return resp


def _read_channel_file(directory: Path, channel_id: str) -> ChannelData:
    path = directory / f"{channel_id}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Channel not found")
    
    try:
        # Читаем файл с правильной кодировкой
        content = path.read_text(encoding="utf-8")
        obj = json.loads(content)
        
        # Валидация через модель с улучшенной обработкой ошибок
        return ChannelData(**obj)
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Invalid JSON format in channel data")
    except UnicodeDecodeError as e:
        logger.error(f"Unicode decode error for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Encoding error in channel data")
    except ValueError as e:
        logger.error(f"Validation error for channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Invalid data format in channel")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading channel {channel_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to read channel data")


@router.get("/channels/movies/{channel_id}", response_model=ChannelData)
async def get_channel_movies(channel_id: str, cache: TTLCache = Depends(get_cache)) -> ChannelData:
    key = _cache_key("/api/channels/movies/{channel_id}", channel_id=channel_id)
    cached = cache.get(key)
    if cached is not None:
        return cached
    data = _read_channel_file(CHANNEL_MOVIES_DIR, channel_id)
    cache.set(key, data)
    return data


@router.get("/channels/cartoons/{channel_id}", response_model=ChannelData)
async def get_channel_cartoons(channel_id: str, cache: TTLCache = Depends(get_cache)) -> ChannelData:
    key = _cache_key("/api/channels/cartoons/{channel_id}", channel_id=channel_id)
    cached = cache.get(key)
    if cached is not None:
        return cached
    data = _read_channel_file(CHANNEL_CARTOONS_DIR, channel_id)
    cache.set(key, data)
    return data


# Добавляем общий эндпоинт для каналов (для совместимости с frontend)
@router.get("/channels", response_model=dict)
async def list_all_channels(cache: TTLCache = Depends(get_cache)) -> dict:
    """Возвращает все доступные каналы (фильмы и мультфильмы)"""
    key = _cache_key("/api/channels")
    cached = cache.get(key)
    if cached is not None:
        return cached
    
    try:
        movies_channels = _list_channels_from_dir(CHANNEL_MOVIES_DIR)
        cartoons_channels = _list_channels_from_dir(CHANNEL_CARTOONS_DIR)
        
        result = {
            "movies": movies_channels,
            "cartoons": cartoons_channels,
            "total": len(movies_channels) + len(cartoons_channels)
        }
        
        cache.set(key, result)
        return result
    except Exception as e:
        logger.error(f"Error fetching channels: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch channels")


# Добавляем health check эндпоинт
@router.get("/health")
async def health_check():
    """Health check эндпоинт для мониторинга"""
    return JSONResponse(
        content={"status": "healthy", "service": "cinema-epg-collector-api"},
        headers={"Content-Type": "application/json; charset=utf-8"}
    )


@router.get("/genres", response_model=dict)
async def list_genres(cache: TTLCache = Depends(get_cache)) -> dict:
    """Получение списка всех жанров"""
    key = _cache_key("/api/genres")
    cached = cache.get(key)
    if cached is not None:
        return cached
    
    try:
        genres = set()
        
        # Собираем жанры из основных файлов с фильмами
        movie_files = ["epg_movies.json", "epg_cartoons.json", "movies.json", "enriched_movies.json"]
        
        for filename in movie_files:
            file_path = MOVIES_DIR / filename
            if file_path.exists():
                try:
                    data = _read_json_file(file_path)
                    if isinstance(data, list):
                        for movie in data:
                            if isinstance(movie, dict) and "epg_data" in movie:
                                epg_data = movie["epg_data"]
                                if isinstance(epg_data, dict) and "genre" in epg_data:
                                    genre = epg_data["genre"]
                                    if isinstance(genre, str) and genre.strip():
                                        # Разделяем жанры по запятым и добавляем каждый
                                        for g in genre.split(","):
                                            g = g.strip()
                                            if g:
                                                genres.add(g)
                except Exception as e:
                    logger.warning(f"Error reading {file_path}: {e}")
        
        result = {"genres": sorted(list(genres))}
        cache.set(key, result)
        return result
    except Exception as e:
        logger.error(f"Error getting genres: {e}")
        raise HTTPException(status_code=500, detail="Failed to get genres")


@router.get("/stats", response_model=dict)
async def get_stats(cache: TTLCache = Depends(get_cache)) -> dict:
    """Получение статистики по фильмам и каналам"""
    key = _cache_key("/api/stats")
    cached = cache.get(key)
    if cached is not None:
        return cached
    
    try:
        # Подсчет общего количества фильмов
        total_movies = 0
        total_channels = 0
        
        # Подсчет фильмов
        for file_path in MOVIES_DIR.glob("*.json"):
            try:
                data = _read_json_file(file_path)
                if isinstance(data, list):
                    total_movies += len(data)
            except Exception as e:
                logger.warning(f"Error reading {file_path}: {e}")
        
        # Подсчет каналов
        total_channels += len(list(CHANNEL_MOVIES_DIR.glob("*.json")))
        total_channels += len(list(CHANNEL_CARTOONS_DIR.glob("*.json")))
        
        result = {
            "total_movies": total_movies,
            "total_channels": total_channels,
            "movies_channels": len(list(CHANNEL_MOVIES_DIR.glob("*.json"))),
            "cartoons_channels": len(list(CHANNEL_CARTOONS_DIR.glob("*.json")))
        }
        
        cache.set(key, result)
        return result
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get statistics")
