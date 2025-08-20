from __future__ import annotations

from typing import Optional, Any, Dict
from urllib.parse import urlencode

import requests

from .config import Config


class TMDBClient:
    """Простой клиент TMDB: поиск фильма по названию и получение URL постера.

    Использует search/movie и собирает полный URL на основе TMDB_IMAGE_BASE.
    """

    def __init__(self, cfg: Config, session: requests.Session):
        self.session = session
        self.api_key = cfg.tmdb_api_key
        self.base_url = cfg.tmdb_base_url.rstrip("/")
        self.image_base = cfg.tmdb_image_base.rstrip("/")

    def is_enabled(self) -> bool:
        return bool(self.api_key)

    def get_poster_url(self, title: str, year: Optional[int] = None, language: str = "ru-RU") -> Optional[str]:
        if not self.is_enabled():
            return None
        if not title:
            return None
        params = {
            "api_key": self.api_key,
            "query": title,
            "include_adult": "true",
            "language": language,
        }
        if year:
            params["year"] = year
        url = f"{self.base_url}/search/movie?{urlencode(params)}"
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            data: Dict[str, Any] = resp.json()
            results = data.get("results") or []
            for r in results:
                poster_path = r.get("poster_path")
                if isinstance(poster_path, str) and poster_path.startswith("/"):
                    return f"{self.image_base}{poster_path}"
            return None
        except Exception:
            return None
