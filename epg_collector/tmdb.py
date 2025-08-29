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

    def get_movie_info(self, title: str, year: Optional[int] = None, language: str = "ru-RU") -> Optional[Dict[str, Any]]:
        """Найти фильм в TMDB и вернуть базовую информацию и постер.

        Возвращаемая структура совместима с тем, что ожидает репозиторий через поле
        `kinopoisk` (мы используем те же ключи, чтобы не менять остальной код):
        {
          "source": "tmdb",
          "name": str,
          "year": int | None,
          "rating_kp": None,
          "rating_imdb": float | None,  # используем vote_average TMDB
          "genres": [str] | None,
          "poster_url": str | None,
          "url": str | None
        }
        """
        if not self.is_enabled() or not title:
            return None
        # 1) Поиск фильма
        params = {
            "api_key": self.api_key,
            "query": title,
            "include_adult": "true",
            "language": language,
        }
        if year:
            params["year"] = year
        search_url = f"{self.base_url}/search/movie?{urlencode(params)}"
        try:
            r = self.session.get(search_url, timeout=30)
            r.raise_for_status()
            js: Dict[str, Any] = r.json()
            results = js.get("results") or []
            if not results:
                return None
            first = results[0]
            movie_id = first.get("id")
            poster_url = None
            if isinstance(first.get("poster_path"), str) and first["poster_path"].startswith("/"):
                poster_url = f"{self.image_base}{first['poster_path']}"
            # Предварительные поля
            name = first.get("title") or first.get("original_title") or title
            release_date = first.get("release_date") or ""
            try:
                tmdb_year = int(release_date.split("-")[0]) if release_date else None
            except Exception:
                tmdb_year = None
            rating_tmdb = first.get("vote_average")
            # 2) Детали фильма для жанров и ссылок
            genres_list = None
            homepage = None
            if movie_id:
                details_params = {
                    "api_key": self.api_key,
                    "language": language,
                }
                details_url = f"{self.base_url}/movie/{movie_id}?{urlencode(details_params)}"
                try:
                    d = self.session.get(details_url, timeout=30)
                    d.raise_for_status()
                    dj: Dict[str, Any] = d.json()
                    g = dj.get("genres") or []
                    if isinstance(g, list):
                        genres_list = [str(x.get("name")) for x in g if isinstance(x, dict) and x.get("name")]
                    homepage = dj.get("homepage")
                except Exception:
                    pass
            return {
                "source": "tmdb",
                "name": name,
                "year": tmdb_year or year,
                "rating_kp": None,
                "rating_imdb": float(rating_tmdb) if isinstance(rating_tmdb, (int, float)) else None,
                "genres": genres_list,
                "poster_url": poster_url,
                "url": homepage,
            }
        except Exception:
            return None
