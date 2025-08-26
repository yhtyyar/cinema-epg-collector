"""Улучшенная система конфигурации с валидацией."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, Optional, List
from pathlib import Path
import logging

from dotenv import load_dotenv
from .exceptions import ConfigurationError

logger = logging.getLogger(__name__)


@dataclass
class DatabaseConfig:
    """Конфигурация базы данных."""
    url: str = "sqlite:///data/app.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


@dataclass
class RedisConfig:
    """Конфигурация Redis для кэширования."""
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    enabled: bool = False


@dataclass
class SecurityConfig:
    """Конфигурация безопасности."""
    secret_key: str = ""
    api_key_header: str = "X-API-Key"
    rate_limit_per_minute: int = 60
    cors_origins: List[str] = field(default_factory=lambda: ["*"])


@dataclass
class MonitoringConfig:
    """Конфигурация мониторинга."""
    enable_metrics: bool = True
    enable_health_checks: bool = True
    metrics_port: int = 9090
    sentry_dsn: Optional[str] = None


@dataclass
class EnhancedConfig:
    """Расширенная конфигурация приложения."""
    
    # Существующие настройки
    iptv_base_url: str
    iptv_params: Dict[str, str]
    iptv_headers: Dict[str, str]
    
    playlist_base_url: str
    playlist_params: Dict[str, str]
    playlist_headers: Dict[str, str]
    playlist_form: Dict[str, str]
    
    http_timeout: int = 30
    http_retries: int = 3
    http_backoff: float = 0.5
    
    cache_enabled: bool = True
    cache_path: str = "cache/http_cache"
    cache_expire: int = 3600
    
    kinopoisk_api_key: Optional[str] = None
    kinopoisk_base_url: str = "https://api.kinopoisk.dev/v1.4"
    
    tmdb_api_key: Optional[str] = None
    tmdb_base_url: str = "https://api.themoviedb.org/3"
    tmdb_image_base: str = "https://image.tmdb.org/t/p/w500"
    
    log_level: str = "INFO"
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cache_ttl: int = 300
    api_cors_origins: List[str] = field(default_factory=lambda: ["*"])
    
    auto_run_pipeline: bool = False
    
    # Новые настройки
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    
    # Настройки обработки
    max_concurrent_requests: int = 10
    batch_size: int = 100
    enable_parallel_processing: bool = True
    
    # Настройки файловой системы
    data_dir: Path = field(default_factory=lambda: Path("data"))
    logs_dir: Path = field(default_factory=lambda: Path("logs"))
    cache_dir: Path = field(default_factory=lambda: Path("cache"))
    
    def __post_init__(self):
        """Валидация конфигурации после инициализации."""
        self._validate_config()
        self._create_directories()
        
    def _validate_config(self):
        """Валидирует конфигурацию."""
        errors = []
        
        # Проверка обязательных URL
        if not self.iptv_base_url:
            errors.append("IPTV_BASE_URL обязателен")
            
        if not self.playlist_base_url:
            errors.append("PLAYLIST_BASE_URL обязателен")
            
        # Проверка портов
        if not (1 <= self.api_port <= 65535):
            errors.append(f"Некорректный API порт: {self.api_port}")
            
        if self.monitoring.enable_metrics and not (1 <= self.monitoring.metrics_port <= 65535):
            errors.append(f"Некорректный порт метрик: {self.monitoring.metrics_port}")
            
        # Проверка таймаутов
        if self.http_timeout <= 0:
            errors.append("HTTP_TIMEOUT должен быть больше 0")
            
        # Проверка ключей API
        if self.kinopoisk_api_key and len(self.kinopoisk_api_key) < 10:
            errors.append("KINOPOISK_API_KEY слишком короткий")
            
        if self.tmdb_api_key and len(self.tmdb_api_key) < 10:
            errors.append("TMDB_API_KEY слишком короткий")
            
        # Проверка безопасности
        if not self.security.secret_key:
            logger.warning("SECRET_KEY не установлен, используется значение по умолчанию")
            self.security.secret_key = "dev-secret-key-change-in-production"
            
        if errors:
            raise ConfigurationError(f"Ошибки конфигурации: {'; '.join(errors)}")
            
    def _create_directories(self):
        """Создает необходимые директории."""
        for directory in [self.data_dir, self.logs_dir, self.cache_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
    @property
    def is_development(self) -> bool:
        """Проверяет, запущено ли приложение в режиме разработки."""
        return os.getenv("ENVIRONMENT", "development").lower() == "development"
        
    @property
    def is_production(self) -> bool:
        """Проверяет, запущено ли приложение в продакшене."""
        return os.getenv("ENVIRONMENT", "development").lower() == "production"


def load_enhanced_config() -> EnhancedConfig:
    """Загружает расширенную конфигурацию."""
    load_dotenv(override=False)
    
    # Базовые настройки IPTV
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
    
    # Настройки плейлиста
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
    
    # Расширенные настройки
    database_config = DatabaseConfig(
        url=os.getenv("DATABASE_URL", "sqlite:///data/app.db"),
        echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
        pool_size=int(os.getenv("DATABASE_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    )
    
    redis_config = RedisConfig(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        password=os.getenv("REDIS_PASSWORD"),
        enabled=os.getenv("REDIS_ENABLED", "false").lower() == "true"
    )
    
    security_config = SecurityConfig(
        secret_key=os.getenv("SECRET_KEY", ""),
        api_key_header=os.getenv("API_KEY_HEADER", "X-API-Key"),
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60")),
        cors_origins=[
            origin.strip() 
            for origin in os.getenv("API_CORS_ORIGINS", "*").split(",") 
            if origin.strip()
        ]
    )
    
    monitoring_config = MonitoringConfig(
        enable_metrics=os.getenv("ENABLE_METRICS", "true").lower() == "true",
        enable_health_checks=os.getenv("ENABLE_HEALTH_CHECKS", "true").lower() == "true",
        metrics_port=int(os.getenv("METRICS_PORT", "9090")),
        sentry_dsn=os.getenv("SENTRY_DSN")
    )
    
    return EnhancedConfig(
        # Базовые настройки
        iptv_base_url=iptv_base_url,
        iptv_params=iptv_params,
        iptv_headers=iptv_headers,
        playlist_base_url=playlist_base_url,
        playlist_params=playlist_params,
        playlist_headers=playlist_headers,
        playlist_form=playlist_form,
        
        http_timeout=int(os.getenv("HTTP_TIMEOUT", "30")),
        http_retries=int(os.getenv("HTTP_RETRIES", "3")),
        http_backoff=float(os.getenv("HTTP_BACKOFF", "0.5")),
        
        cache_enabled=os.getenv("CACHE_ENABLED", "true").lower() == "true",
        cache_path=os.getenv("CACHE_PATH", "cache/http_cache"),
        cache_expire=int(os.getenv("CACHE_EXPIRE", "3600")),
        
        kinopoisk_api_key=os.getenv("KINOPOISK_API_KEY"),
        kinopoisk_base_url=os.getenv("KINOPOISK_BASE_URL", "https://api.kinopoisk.dev/v1.4"),
        
        tmdb_api_key=os.getenv("TMDB_API_KEY"),
        tmdb_base_url=os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3"),
        tmdb_image_base=os.getenv("TMDB_IMAGE_BASE", "https://image.tmdb.org/t/p/w500"),
        
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        
        api_host=os.getenv("API_HOST", "0.0.0.0"),
        api_port=int(os.getenv("API_PORT", "8000")),
        api_cache_ttl=int(os.getenv("API_CACHE_TTL", "300")),
        
        auto_run_pipeline=os.getenv("AUTO_RUN_PIPELINE", "false").lower() == "true",
        
        # Расширенные настройки
        database=database_config,
        redis=redis_config,
        security=security_config,
        monitoring=monitoring_config,
        
        max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "10")),
        batch_size=int(os.getenv("BATCH_SIZE", "100")),
        enable_parallel_processing=os.getenv("ENABLE_PARALLEL_PROCESSING", "true").lower() == "true",
        
        data_dir=Path(os.getenv("DATA_DIR", "data")),
        logs_dir=Path(os.getenv("LOGS_DIR", "logs")),
        cache_dir=Path(os.getenv("CACHE_DIR", "cache")),
    )
