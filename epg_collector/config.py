from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, Optional, List
from dotenv import load_dotenv


@dataclass
class Config:
    # IPTV
    iptv_base_url: str
    iptv_params: Dict[str, str]
    iptv_headers: Dict[str, str]

    # HTTP
    http_timeout: int = 30
    http_retries: int = 3
    http_backoff: float = 0.5

    # Cache
    cache_enabled: bool = True
    cache_path: str = "cache/http_cache"
    cache_expire: int = 3600


    # TMDB (опционально)
    tmdb_api_key: Optional[str] = None
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_image_base: str = "https://image.tmdb.org/t/p/w500"

    # Logging
    log_level: str = "INFO"

    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cache_ttl: int = 300
    api_cors_origins: List[str] = None
    # Pipeline
    auto_run_pipeline: bool = False  # Changed default to False


def load_config() -> Config:
    """Загрузка конфигурации из .env и переменных окружения."""
    load_dotenv(override=False)

    iptv_base_url = os.getenv("IPTV_BASE_URL", "https://pl.iptv2021.com/api/v4/epg")
    iptv_params = {
        "id": os.getenv("IPTV_PARAMS_ID", "17305"),
        "tz": os.getenv("IPTV_PARAMS_TZ", "3"),
        "epg_from": os.getenv("IPTV_PARAMS_EPG_FROM", "-7"),
        "epg_limit": os.getenv("IPTV_PARAMS_EPG_LIMIT", "14"),
        "grouping": os.getenv("IPTV_PARAMS_GROUPING", "1"),
        "region": os.getenv("IPTV_PARAMS_REGION", "0"),
        "lang": os.getenv("IPTV_PARAMS_LANG", "ru"),
    }
    iptv_headers = {
        "Host": os.getenv("IPTV_HEADER_HOST", "pl.iptv2021.com"),
        "User-Agent": os.getenv("IPTV_HEADER_UA", "Mozilla/5.0"),
        "x-lhd-agent": os.getenv("IPTV_HEADER_X_LHD_AGENT", ""),
        "x-token": os.getenv("IPTV_HEADER_X_TOKEN", ""),
    }

    http_timeout = int(os.getenv("HTTP_TIMEOUT", 30))
    http_retries = int(os.getenv("HTTP_RETRIES", 3))
    http_backoff = float(os.getenv("HTTP_BACKOFF", 0.5))

    cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    cache_path = os.getenv("CACHE_PATH", "cache/http_cache")
    cache_expire = int(os.getenv("CACHE_EXPIRE", 3600))


    tmdb_api_key = os.getenv("TMDB_API_KEY") or None
    tmdb_base_url = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    tmdb_image_base = os.getenv("TMDB_IMAGE_BASE", "https://image.tmdb.org/t/p/w500")

    log_level = os.getenv("LOG_LEVEL", "INFO")

    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", 8000))
    api_cache_ttl = int(os.getenv("API_CACHE_TTL", 300))
    cors_raw = os.getenv("API_CORS_ORIGINS", "*")
    api_cors_origins = [o.strip() for o in cors_raw.split(",") if o.strip()] if cors_raw else ["*"]

    auto_run_pipeline = os.getenv("AUTO_RUN_PIPELINE", "false").lower() == "true"  # Changed default to false

    return Config(
        iptv_base_url=iptv_base_url,
        iptv_params=iptv_params,
        iptv_headers=iptv_headers,
        http_timeout=http_timeout,
        http_retries=http_retries,
        http_backoff=http_backoff,
        cache_enabled=cache_enabled,
        cache_path=cache_path,
        cache_expire=cache_expire,
        tmdb_api_key=tmdb_api_key,
        tmdb_base_url=tmdb_base_url,
        tmdb_image_base=tmdb_image_base,
        log_level=log_level,
        api_host=api_host,
        api_port=api_port,
        api_cache_ttl=api_cache_ttl,
        api_cors_origins=api_cors_origins,
        auto_run_pipeline=auto_run_pipeline,
    )