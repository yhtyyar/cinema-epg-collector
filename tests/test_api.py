from __future__ import annotations

import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Ensure project root is on sys.path for 'epg_collector' imports
PROJECT_ROOT = str(Path(__file__).resolve().parents[1])
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient

from epg_collector.api.app import create_app
from epg_collector.api.dependencies import get_repository
from epg_collector.api.repository import MoviesRepository


class FakeMoviesRepository(MoviesRepository):
    """Фейковый репозиторий, использующий тот же интерфейс и нормализацию,
    что и боевой `MoviesRepository`, но с данными в памяти.
    """

    def __init__(self) -> None:
        # Не вызываем загрузку из файла, сразу кладём сырые элементы
        self._path = None  # type: ignore
        self._raw: List[Dict[str, Any]] = [
            {
                "id": "1",
                "title": "Невидимка",
                "preview": None,
                "mskdatetimestart": "2024-08-20 12:00:00",
                "kinopoisk": {
                    "name": "Невидимка",
                    "year": 2019,
                    "rating_kp": 6.2,
                    "genres": ["Фэнтези", "Приключения"],
                },
                "poster_local": "data/posters/1.jpg",
                "poster_source": "kinopoisk",
            },
            {
                "id": "2",
                "title": "Боксёр",
                "preview": None,
                "timestart": 1724152800,  # epoch
                "kinopoisk": {
                    "name": "Boxer",
                    "year": 2020,
                    "rating_kp": 7.4,
                    "genres": ["Боевик", "Драма"],
                },
                "poster_local": None,
                "poster_source": "tmdb",
            },
            {
                "id": "3",
                "title": "Комедия дня",
                "preview": None,
                "timestart": 1724156400,
                "kinopoisk": {
                    "name": "Daily Fun",
                    "year": 2018,
                    "rating_kp": 5.8,
                    "genres": ["Комедия"],
                },
                "poster_local": None,
                "poster_source": "preview",
            },
        ]


def make_app_with_fakes():
    app = create_app()
    app.dependency_overrides[get_repository] = lambda: FakeMoviesRepository()
    return app


def test_healthz_ok():
    app = make_app_with_fakes()
    with TestClient(app) as client:
        resp = client.get("/healthz")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


def test_list_movies_basic_pagination_and_shape():
    app = make_app_with_fakes()
    with TestClient(app) as client:
        resp = client.get("/api/movies", params={"page": 1, "per_page": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"movies", "pagination"}
        assert len(data["movies"]) == 2
        pag = data["pagination"]
        assert pag["page"] == 1
        assert pag["per_page"] == 2
        assert pag["total"] >= 3
        assert pag["pages"] >= 2
        # Проверим маппинг локального постера на /static/
        first = data["movies"][0]
        # Не все фильмы имеют локальный постер, найдём тот, у кого он есть
        has_local = any(m.get("kinopoisk_data", {}).get("poster_url", "").startswith("/static/") for m in data["movies"])
        assert has_local is True


def test_get_movie_by_id_ok():
    app = make_app_with_fakes()
    with TestClient(app) as client:
        resp = client.get("/api/movies/2")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == "2"
        assert body["kinopoisk_data"]["year"] == 2020


def test_get_movie_404():
    app = make_app_with_fakes()
    with TestClient(app) as client:
        resp = client.get("/api/movies/999")
        assert resp.status_code == 404


def test_search_matches_epg_or_kp():
    app = make_app_with_fakes()
    with TestClient(app) as client:
        # Поиск по EPG title
        r1 = client.get("/api/movies/search", params={"q": "невидимка", "per_page": 10})
        assert r1.status_code == 200
        ids1 = [m["id"] for m in r1.json()["movies"]]
        assert "1" in ids1
        # Поиск по KP name
        r2 = client.get("/api/movies/search", params={"q": "boxer", "per_page": 10})
        assert r2.status_code == 200
        ids2 = [m["id"] for m in r2.json()["movies"]]
        assert "2" in ids2


def test_filters_genre_year_rating_source():
    app = make_app_with_fakes()
    with TestClient(app) as client:
        # Жанр Боевик -> должен вернуть фильм с id=2
        r_genre = client.get("/api/movies", params={"genre": "Боевик", "per_page": 50})
        assert r_genre.status_code == 200
        ids = [m["id"] for m in r_genre.json()["movies"]]
        assert ids == ["2"]

        # Год 2019 -> id=1
        r_year = client.get("/api/movies", params={"year": 2019, "per_page": 50})
        assert r_year.status_code == 200
        ids = [m["id"] for m in r_year.json()["movies"]]
        assert ids == ["1"]

        # Рейтинг >= 6.0 -> id=1 и id=2 (5.8 отсечётся)
        r_rating = client.get("/api/movies", params={"rating_gte": 6.0, "per_page": 50})
        assert r_rating.status_code == 200
        ids = [m["id"] for m in r_rating.json()["movies"]]
        assert set(ids) == {"1", "2"}

        # Источник постера tmdb -> id=2
        r_source = client.get("/api/movies", params={"source": "tmdb", "per_page": 50})
        assert r_source.status_code == 200
        ids = [m["id"] for m in r_source.json()["movies"]]
        assert ids == ["2"]
