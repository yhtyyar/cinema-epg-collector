from __future__ import annotations

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import requests_cache

from .config import Config

logger = logging.getLogger(__name__)


def _build_retry(total: int, backoff: float) -> Retry:
    return Retry(
        total=total,
        backoff_factor=backoff,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )


def create_session(cfg: Config) -> requests.Session:
    """Создаёт requests.Session с кэшем, retry и таймаутами по умолчанию."""
    if cfg.cache_enabled:
        requests_cache.install_cache(
            cache_name=cfg.cache_path,
            backend="sqlite",
            expire_after=cfg.cache_expire,
        )
        logger.info("Requests cache enabled: %s (expire %ss)", cfg.cache_path, cfg.cache_expire)

    session = requests.Session()

    retry = _build_retry(cfg.http_retries, cfg.http_backoff)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # Defaults: headers may be extended per-request
    session.headers.update({"User-Agent": cfg.iptv_headers.get("User-Agent", "Mozilla/5.0")})

    # Attach default timeout via wrapper
    _original_request = session.request

    def _request_with_timeout(method: str, url: str, **kwargs):
        timeout = kwargs.pop("timeout", cfg.http_timeout)
        return _original_request(method, url, timeout=timeout, **kwargs)

    session.request = _request_with_timeout  # type: ignore
    return session
