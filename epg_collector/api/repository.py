from __future__ import annotations

import json
import pathlib
from typing import Any, Dict, List, Optional, Tuple

from epg_collector.api.models import EPGData, TMDBData, Metadata, Movie


class MoviesRepository:
    def __init__(self, data_path: str = "data/enriched_movies.json") -> None:
        self._path = pathlib.Path(data_path)
        self._raw: List[Dict[str, Any]] = []
        self._mtime: Optional[float] = None
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            self._raw = []
            self._mtime = None
            return
        self._raw = json.loads(self._path.read_text(encoding="utf-8"))
        try:
            self._mtime = self._path.stat().st_mtime
        except Exception:
            # Если не удалось получить mtime, оставляем предыдущее значение
            pass

    def _reload_if_changed(self) -> None:
        """Перечитывает данные, если файл обновился."""
        try:
            if not self._path.exists():
                if self._raw:
                    # Файл удалён — очистим данные
                    self._raw = []
                self._mtime = None
                return
            current = self._path.stat().st_mtime
            if self._mtime is None or current != self._mtime:
                self._load()
        except Exception:
            # Никогда не падаем из‑за ошибок перезагрузки
            pass

    def _to_iso(self, val: Optional[str], epoch: Optional[int]) -> Optional[str]:
        if val:
            # convert 'YYYY-MM-DD HH:MM:SS' -> ISO 'YYYY-MM-DDTHH:MM:SS'
            return val.replace(" ", "T")
        if epoch:
            # seconds since epoch to ISO (UTC)
            from datetime import datetime, timezone
            return datetime.fromtimestamp(epoch, tz=timezone.utc).isoformat()
        return None

    def _poster_url(self, poster_local: Optional[str], tmdb_data: Optional[Dict[str, Any]]) -> Optional[str]:
        # Возвращаем ТОЛЬКО локально сохранённые постеры, отданные через /static.
        # Это исключает внешние URL (TMDB), которые часто блокируются/не грузятся в браузере.
        if poster_local:
            # Map local file within data/ to /static path so it is served by the API
            # Example: data/posters/xyz.jpg -> /static/posters/xyz.jpg
            norm = poster_local.replace("\\", "/")
            if norm.startswith("data/"):
                relative = norm[len("data/"):]
                return "/static/" + relative
            return "/static/" + norm
        return None

    def _normalize(self, item: Dict[str, Any]) -> Movie:
        tmdb_data = item.get("tmdb_data") or {}
        rating = tmdb_data.get("rating_imdb")
        try:
            rating_val: Optional[float] = float(rating) if rating is not None else None
        except (TypeError, ValueError):
            rating_val = None

        genres = tmdb_data.get("genres")
        if isinstance(genres, list):
            genres_list = [str(g) for g in genres]
        else:
            genres_list = None

        epg = EPGData(
            title=item.get("title"),
            description=item.get("desc"),
            broadcast_time=self._to_iso(item.get("mskdatetimestart"), item.get("timestart")),
            preview_image=item.get("preview"),
        )
        tmdb = None
        if tmdb_data:
            tmdb = TMDBData(
                title=tmdb_data.get("name"),
                original_title=None,
                year=tmdb_data.get("year"),
                rating=rating_val,
                description=None,
                poster_url=self._poster_url(item.get("poster_local"), tmdb_data),
                genres=genres_list,
                duration=None,
            )
        else:
            tmdb = TMDBData(
                title=None,
                original_title=None,
                year=None,
                rating=None,
                description=None,
                poster_url=self._poster_url(item.get("poster_local"), None),
                genres=None,
                duration=None,
            )

        meta = Metadata(
            created_at=None,
            updated_at=None,
            source="enriched",
        )

        return Movie(
            id=str(item.get("id")),
            epg_data=epg,
            tmdb_data=tmdb,
            metadata=meta,
        )

    def get_by_id(self, movie_id: str) -> Optional[Movie]:
        self._reload_if_changed()
        for it in self._raw:
            if str(it.get("id")) == str(movie_id):
                return self._normalize(it)
        return None

    def list_movies(
        self,
        page: int = 1,
        per_page: int = 50,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        rating_gte: Optional[float] = None,
        source: Optional[str] = None,
        search_q: Optional[str] = None,
    ) -> Tuple[List[Movie], int]:
        """Возвращает (movies, total) с фильтрацией и пагинацией.

        Если указан search_q, выполняется поиск по epg.title и tmdb.name.
        """
        self._reload_if_changed()
        data = self._raw

        # Фильтры
        def predicate(it: Dict[str, Any]) -> bool:
            if genre:
                tmdb = it.get("tmdb_data") or {}
                genres = tmdb.get("genres") or []
                if isinstance(genres, list):
                    if genre not in [str(g) for g in genres]:
                        return False
                else:
                    return False
            if year is not None:
                tmdb = it.get("tmdb_data") or {}
                if tmdb.get("year") != year:
                    return False
            if rating_gte is not None:
                tmdb = it.get("tmdb_data") or {}
                rv = tmdb.get("rating_imdb")
                try:
                    rvf = float(rv) if rv is not None else None
                except (TypeError, ValueError):
                    rvf = None
                if rvf is None or rvf < rating_gte:
                    return False
            if source:
                src = it.get("poster_source")
                if src != source:
                    return False
            if search_q:
                q = str(search_q).lower()
                epg_title = str(it.get("title") or "").lower()
                tmdb_title = str((it.get("tmdb_data") or {}).get("name") or "").lower()
                if q not in epg_title and q not in tmdb_title:
                    return False
            return True

        filtered = [it for it in data if predicate(it)]
        total = len(filtered)

        # Пагинация
        if per_page <= 0:
            per_page = 50
        start = (page - 1) * per_page
        end = start + per_page
        page_items = filtered[start:end]

        movies = [self._normalize(it) for it in page_items]
        return movies, total
