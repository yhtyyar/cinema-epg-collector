from __future__ import annotations

import logging
import os
import json
import time
import hashlib
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .config import Config

logger = logging.getLogger(__name__)


class SimpleFileCache:
    """Простое файловое кэширование HTTP запросов без SQLite."""
    
    def __init__(self, cache_dir: str, expire_after: int):
        self.cache_dir = Path(cache_dir)
        self.expire_after = expire_after
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, url: str, params: dict = None) -> str:
        """Генерирует ключ кэша для URL и параметров."""
        cache_data = f"{url}_{params or {}}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def get(self, url: str, params: dict = None) -> dict | None:
        """Получает данные из кэша если они не устарели."""
        cache_key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Проверяем срок действия
            if time.time() - cached_data['timestamp'] > self.expire_after:
                cache_file.unlink(missing_ok=True)
                return None
                
            return cached_data['response']
        except (json.JSONDecodeError, KeyError, OSError):
            cache_file.unlink(missing_ok=True)
            return None
    
    def set(self, url: str, response_data: dict, params: dict = None):
        """Сохраняет данные в кэш."""
        cache_key = self._get_cache_key(url, params)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cached_data = {
            'timestamp': time.time(),
            'response': response_data,
            'url': url,
            'params': params
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.warning("Failed to save cache for %s: %s", url, e)


def _build_retry(total: int, backoff: float) -> Retry:
    return Retry(
        total=total,
        backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )


def create_session(cfg: Config) -> requests.Session:
    """Создаёт requests.Session с файловым кэшем, retry и таймаутами по умолчанию."""
    cache = None
    if cfg.cache_enabled:
        cache = SimpleFileCache(cfg.cache_path, cfg.cache_expire)
        logger.info("File cache enabled: %s (expire %ss)", cfg.cache_path, cfg.cache_expire)

    session = requests.Session()

    retry = _build_retry(cfg.http_retries, cfg.http_backoff)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Defaults: headers may be extended per-request
    session.headers.update({"User-Agent": cfg.iptv_headers.get("User-Agent", "Mozilla/5.0")})

    # Attach default timeout and caching via wrapper
    _original_request = session.request

    def _request_with_timeout_and_cache(method: str, url: str, **kwargs):
        timeout = kwargs.pop("timeout", cfg.http_timeout)
        
        # Попробуем получить из кэша для GET запросов
        if cache and method.upper() == 'GET':
            params = kwargs.get('params')
            cached_response = cache.get(url, params)
            if cached_response:
                # Создаем mock response объект
                mock_response = requests.Response()
                mock_response._content = json.dumps(cached_response).encode('utf-8')
                mock_response.status_code = 200
                mock_response.headers['Content-Type'] = 'application/json'
                logger.debug("Cache hit for %s", url)
                return mock_response
        
        # Выполняем запрос
        response = _original_request(method, url, timeout=timeout, **kwargs)
        
        # Сохраняем в кэш успешные GET запросы
        if cache and method.upper() == 'GET' and response.status_code == 200:
            try:
                response_data = response.json()
                params = kwargs.get('params')
                cache.set(url, response_data, params)
                logger.debug("Cached response for %s", url)
            except (json.JSONDecodeError, ValueError):
                # Не JSON ответ, не кэшируем
                pass
        
        return response

    session.request = _request_with_timeout_and_cache  # type: ignore
    return session
