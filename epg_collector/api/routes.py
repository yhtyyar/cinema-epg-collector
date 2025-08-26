from __future__ import annotations

import math
from typing import Optional, List
from pathlib import Path
import json

from fastapi import APIRouter, Depends, HTTPException, Query

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

router = APIRouter(prefix="/api", tags=["movies"])


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


# --- Channels (per-channel JSON) ---

CHANNEL_MOVIES_DIR = Path("data/channel_json/movies")
CHANNEL_CARTOONS_DIR = Path("data/channel_json/cartoons")


def _list_channels_from_dir(directory: Path) -> List[ChannelItem]:
    channels: List[ChannelItem] = []
    if not directory.exists():
        return channels
    for p in sorted(directory.glob("*.json")):
        try:
            obj = json.loads(p.read_text(encoding="utf-8"))
            cid = str(obj.get("our_id") or p.stem)
            cnt = int(obj.get("count") or (len(obj.get("items", [])) if isinstance(obj.get("items"), list) else 0))
            channels.append(ChannelItem(id=cid, count=cnt))
        except Exception:
            # Пропускаем битые файлы
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
        obj = json.loads(path.read_text(encoding="utf-8"))
        # Валидация через модель
        return ChannelData(**obj)
    except HTTPException:
        raise
    except Exception:
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
