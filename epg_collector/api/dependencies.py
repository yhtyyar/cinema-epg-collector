from __future__ import annotations

from functools import lru_cache
from typing import Optional

from fastapi import Depends

from epg_collector.config import Config, load_config
from epg_collector.api.cache import TTLCache
from epg_collector.api.repository import MoviesRepository


@lru_cache(maxsize=1)
def get_settings() -> Config:
    return load_config()


_cache_instance: Optional[TTLCache] = None
def get_cache(settings: Config = Depends(get_settings)) -> TTLCache:
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = TTLCache(ttl_seconds=settings.api_cache_ttl)
    return _cache_instance


_repo_instance: Optional[MoviesRepository] = None
def get_repository(settings: Config = Depends(get_settings)) -> MoviesRepository:
    global _repo_instance
    if _repo_instance is None:
        _repo_instance = MoviesRepository(data_path="data/enriched_movies.json")
    return _repo_instance
