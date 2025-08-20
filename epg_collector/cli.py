from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any

import typer
from rich import print
from rich.progress import track

from .config import load_config
from .http_client import create_session
from .iptv_api import fetch_epg
from .filters import filter_movies_by_category
from .kinopoisk import KinoPoiskClient
from .logging_config import setup_logging
from .posters import download_poster, is_valid_image_file
from .tmdb import TMDBClient

app = typer.Typer(help="IPTV EPG Collector CLI")

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

RAW_PATH = DATA_DIR / "raw_epg.json"
MOVIES_PATH = DATA_DIR / "movies.json"
ENRICHED_PATH = DATA_DIR / "enriched_movies.json"
POSTERS_DIR = DATA_DIR / "posters"


@app.command()
def fetch_epg_cmd() -> None:
    """Загрузить EPG из IPTV API и сохранить в data/raw_epg.json."""
    cfg = load_config()
    setup_logging(cfg.log_level)
    session = create_session(cfg)

    epg = fetch_epg(cfg, session)
    RAW_PATH.write_text(json.dumps(epg, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[green]Сохранено[/green] {len(epg)} элементов в {RAW_PATH}")


@app.command()
def filter_movies_cmd() -> None:
    """Отфильтровать фильмы (категория содержит 'Х/ф') и сохранить в data/movies.json."""
    cfg = load_config()
    setup_logging(cfg.log_level)

    if not RAW_PATH.exists():
        print(f"[yellow]{RAW_PATH} не найден. Сначала выполните fetch-epg[/yellow]")
        raise typer.Exit(code=1)

    data = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        print("[red]Ожидался список в raw_epg.json[/red]")
        raise typer.Exit(code=1)

    # Поддержка двух форматов:
    # 1) Плоский список элементов EPG
    # 2) Список дней, где внутри ключа "data" хранится список элементов EPG
    items: List[Dict[str, Any]] = []
    for elem in data:
        if isinstance(elem, dict) and isinstance(elem.get("data"), list):
            for sub in elem["data"]:
                if isinstance(sub, dict):
                    items.append(sub)
        elif isinstance(elem, dict):
            items.append(elem)

    movies = filter_movies_by_category(items)
    MOVIES_PATH.write_text(json.dumps(movies, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[green]Сохранено[/green] {len(movies)} фильмов в {MOVIES_PATH}")


@app.command()
def enrich(limit: int = typer.Option(None, help="Ограничить количество фильмов для обогащения")) -> None:
    """Обогатить фильмы информацией КиноПоиска и сохранить в data/enriched_movies.json."""
    cfg = load_config()
    setup_logging(cfg.log_level)
    session = create_session(cfg)
    kp = KinoPoiskClient(cfg, session)
    tmdb = TMDBClient(cfg, session)

    if not MOVIES_PATH.exists():
        print(f"[yellow]{MOVIES_PATH} не найден. Сначала выполните filter-movies[/yellow]")
        raise typer.Exit(code=1)

    movies: List[Dict[str, Any]] = json.loads(MOVIES_PATH.read_text(encoding="utf-8"))
    if limit is not None:
        movies = movies[:limit]

    # Загрузим предыдущие результаты обогащения, чтобы переиспользовать уже скачанные постеры и данные
    prev_by_id: Dict[Any, Dict[str, Any]] = {}
    if ENRICHED_PATH.exists():
        try:
            prev_items: List[Dict[str, Any]] = json.loads(ENRICHED_PATH.read_text(encoding="utf-8"))
            for it in prev_items:
                key = it.get("id") or (it.get("title"), it.get("timestart"))
                if key is not None:
                    prev_by_id[key] = it
        except Exception:
            prev_by_id = {}

    enriched: List[Dict[str, Any]] = []
    for item in track(movies, description="Обогащение КиноПоиском и загрузка постеров"):
        title = item.get("title") or item.get("name")
        # Переиспользование постеров/данных, если ранее уже были сохранены и файл существует
        prev_key = item.get("id") or (item.get("title"), item.get("timestart"))
        prev = prev_by_id.get(prev_key) if prev_key is not None else None
        if prev:
            prev_poster = prev.get("poster_local")
            prev_source = prev.get("poster_source")
            if isinstance(prev_poster, str) and prev_poster:
                prev_path = Path(prev_poster)
                if is_valid_image_file(prev_path):
                    enriched.append({**item, "kinopoisk": prev.get("kinopoisk"), "poster_local": prev_poster, "poster_source": prev_source})
                    continue

        if not isinstance(title, str) or not title.strip():
            enriched.append({**item, "kinopoisk": None, "poster_local": None})
            continue
        info = kp.get_movie_info(title)

        # Подбор URL постера: сначала КиноПоиск, затем TMDB, затем превью из EPG
        candidate_urls: List[Dict[str, Any]] = []  # {url, source}
        if isinstance(info, dict):
            pu = info.get("poster_url")
            if isinstance(pu, str) and pu.startswith("http"):
                candidate_urls.append({"url": pu, "source": "kinopoisk"})
        # TMDB как альтернативный источник (если доступен ключ)
        if tmdb.is_enabled():
            year = None
            if isinstance(info, dict) and isinstance(info.get("year"), int):
                year = info.get("year")
            tmdb_url = tmdb.get_poster_url(title, year=year)
            if isinstance(tmdb_url, str) and tmdb_url.startswith("http"):
                candidate_urls.append({"url": tmdb_url, "source": "tmdb"})
        prev_url = item.get("preview")
        if isinstance(prev_url, str) and prev_url.startswith("http"):
            candidate_urls.append({"url": prev_url, "source": "preview"})

        poster_local: Any = None
        poster_source: Any = None
        for cand in candidate_urls:
            url = cand["url"]
            poster_local = download_poster(
                session=session,
                url=url,
                posters_dir=POSTERS_DIR,
                title=title,
                epg_id=item.get("id"),
            )
            if poster_local:
                poster_source = cand.get("source")
                break

        enriched.append({**item, "kinopoisk": info, "poster_local": poster_local, "poster_source": poster_source})

    ENRICHED_PATH.write_text(json.dumps(enriched, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[green]Сохранено[/green] {len(enriched)} элементов в {ENRICHED_PATH}")


@app.command()
def run_all() -> None:
    """Полный цикл: загрузка EPG, фильтрация фильмов, обогащение."""
    fetch_epg_cmd()
    filter_movies_cmd()
    enrich()


if __name__ == "__main__":
    app()
