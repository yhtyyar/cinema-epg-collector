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

    # Playlist
    playlist_base_url: str
    playlist_params: Dict[str, str]
    playlist_headers: Dict[str, str]
    playlist_form: Dict[str, str]

    # HTTP
    http_timeout: int = 30
    http_retries: int = 3
    http_backoff: float = 0.5

    # Cache
    cache_enabled: bool = True
    cache_path: str = "cache/http_cache"
    cache_expire: int = 3600

    # Kinopoisk
    kinopoisk_api_key: Optional[str] = None
    kinopoisk_base_url: str = "https://api.kinopoisk.dev/v1.4"

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
    auto_run_pipeline: bool = False


def load_config() -> Config:
    """Загрузка конфигурации из .env и переменных окружения."""
    load_dotenv(override=False)

    iptv_base_url = os.getenv("IPTV_BASE_URL", "https://pl.iptv2021.com/api/v4/epg")
    iptv_params = {
        "id": os.getenv("IPTV_PARAMS_ID", "126"),
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

    # Playlist API (POST form-urlencoded)
    playlist_base_url = os.getenv("PLAYLIST_BASE_URL", "https://pl.iptv2021.com/api/v4/playlist")
    playlist_params = {
        "tz": os.getenv("PLAYLIST_PARAMS_TZ", "3"),
        "region": os.getenv("PLAYLIST_PARAMS_REGION", "0"),
        "native_region_only": os.getenv("PLAYLIST_PARAMS_NATIVE_REGION_ONLY", "1"),
        "limit": os.getenv("PLAYLIST_PARAMS_LIMIT", "0"),
        "page": os.getenv("PLAYLIST_PARAMS_PAGE", "1"),
        "epg": os.getenv("PLAYLIST_PARAMS_EPG", "0"),
        "installts": os.getenv("PLAYLIST_PARAMS_INSTALLTS", ""),
        "needCategories": os.getenv("PLAYLIST_PARAMS_NEED_CATEGORIES", "1"),
        "podcasts": os.getenv("PLAYLIST_PARAMS_PODCASTS", "1"),
    }
    # По умолчанию используем те же значения, что и для IPTV, если специальные не заданы
    playlist_headers = {
        "Host": os.getenv("PLAYLIST_HEADER_HOST", os.getenv("IPTV_HEADER_HOST", "pl.iptv2021.com")),
        "User-Agent": os.getenv("PLAYLIST_HEADER_UA", os.getenv("IPTV_HEADER_UA", "Mozilla/5.0")),
        "x-lhd-agent": os.getenv("PLAYLIST_HEADER_X_LHD_AGENT", os.getenv("IPTV_HEADER_X_LHD_AGENT", "")),
        "x-token": os.getenv("PLAYLIST_HEADER_X_TOKEN", os.getenv("IPTV_HEADER_X_TOKEN", "")),
        "Content-Type": "application/x-www-form-urlencoded",
    }
    playlist_form = {
        "subs_packs": os.getenv("PLAYLIST_FORM_SUBS_PACKS", "[]"),
        "y_subs_packs": os.getenv("PLAYLIST_FORM_Y_SUBS_PACKS", "[]"),
        "payload": os.getenv("PLAYLIST_FORM_PAYLOAD", ""),
    }

    http_timeout = int(os.getenv("HTTP_TIMEOUT", 30))
    http_retries = int(os.getenv("HTTP_RETRIES", 3))
    http_backoff = float(os.getenv("HTTP_BACKOFF", 0.5))

    cache_enabled = os.getenv("CACHE_ENABLED", "true").lower() == "true"
    cache_path = os.getenv("CACHE_PATH", "cache/http_cache")
    cache_expire = int(os.getenv("CACHE_EXPIRE", 3600))

    kinopoisk_api_key = os.getenv("KINOPOISK_API_KEY") or None
    kinopoisk_base_url = os.getenv("KINOPOISK_BASE_URL", "https://api.kinopoisk.dev/v1.4")

    tmdb_api_key = os.getenv("TMDB_API_KEY") or None
    tmdb_base_url = os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3")
    tmdb_image_base = os.getenv("TMDB_IMAGE_BASE", "https://image.tmdb.org/t/p/w500")

    log_level = os.getenv("LOG_LEVEL", "INFO")

    api_host = os.getenv("API_HOST", "0.0.0.0")
    api_port = int(os.getenv("API_PORT", 8000))
    api_cache_ttl = int(os.getenv("API_CACHE_TTL", 300))
    cors_raw = os.getenv("API_CORS_ORIGINS", "*")
    api_cors_origins = [o.strip() for o in cors_raw.split(",") if o.strip()] if cors_raw else ["*"]

    auto_run_pipeline = os.getenv("AUTO_RUN_PIPELINE", "false").lower() == "true"

    return Config(
        iptv_base_url=iptv_base_url,
        iptv_params=iptv_params,
        iptv_headers=iptv_headers,
        playlist_base_url=playlist_base_url,
        playlist_params=playlist_params,
        playlist_headers=playlist_headers,
        playlist_form=playlist_form,
        http_timeout=http_timeout,
        http_retries=http_retries,
        http_backoff=http_backoff,
        cache_enabled=cache_enabled,
        cache_path=cache_path,
        cache_expire=cache_expire,
        kinopoisk_api_key=kinopoisk_api_key,
        kinopoisk_base_url=kinopoisk_base_url,
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
