from __future__ import annotations

import math
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from epg_collector.api.models import MoviesResponse, Pagination, Movie
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


@router.get("/movies/{movie_id}", response_model=Movie)
async def get_movie(
    movie_id: str,
    repo: MoviesRepository = Depends(get_repository),
) -> Movie:
    movie = repo.get_by_id(movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


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
