from __future__ import annotations

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import typer
from rich import print
from rich.progress import track

from .config import load_config
from .http_client import create_session
from .iptv_api import fetch_epg, fetch_epg_for_channel
from .playlist_api import fetch_playlist
from .filters import filter_movies_by_category, filter_cartoons_by_category, filter_movies_epg
from .kinopoisk import KinoPoiskClient
from .logging_config import setup_logging
from .posters import download_poster, is_valid_image_file
from .tmdb import TMDBClient

app = typer.Typer(help="IPTV EPG Collector CLI")

DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

RAW_PATH = DATA_DIR / "raw_epg.json"
RAW_PLAYLIST_PATH = DATA_DIR / "raw_playlist.json"
MOVIES_PATH = DATA_DIR / "movies.json"
ENRICHED_PATH = DATA_DIR / "enriched_movies.json"
POSTERS_DIR = DATA_DIR / "posters"
EPG_CHANNELS_DIR = DATA_DIR / "epg_channels"
EPG_CHANNELS_DIR.mkdir(parents=True, exist_ok=True)
EPG_FILTERED_DIR = DATA_DIR / "epg_channels_filtered"
EPG_FILTERED_DIR.mkdir(parents=True, exist_ok=True)
EPG_MOVIES_PATH = DATA_DIR / "epg_movies.json"
EPG_CARTOONS_DIR = DATA_DIR / "epg_channels_cartoons"
EPG_CARTOONS_DIR.mkdir(parents=True, exist_ok=True)
EPG_CARTOONS_PATH = DATA_DIR / "epg_cartoons.json"


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
def fetch_playlist_cmd() -> None:
    """Загрузить плейлист (playlist API) и сохранить в data/raw_playlist.json."""
    cfg = load_config()
    setup_logging(cfg.log_level)
    session = create_session(cfg)

    data = fetch_playlist(cfg, session)
    # Сохраняем как есть (словарь или список), с Unicode и отступами
    RAW_PLAYLIST_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    # Пытаемся вывести краткую статистику
    size = 0
    try:
        if isinstance(data, dict):
            # Популярные ключи: categories, channels, results и т.п.
            for k in ("categories", "channels", "data", "results", "items"):
                v = data.get(k)
                if isinstance(v, list):
                    size = len(v)
                    break
    except Exception:
        size = 0
    print(f"[green]Сохранено[/green] {size} элементов (если применимо) в {RAW_PLAYLIST_PATH}")


def _extract_channel_ids_from_playlist(obj: Any) -> List[str]:
    """Пытается извлечь идентификаторы каналов из структуры плейлиста.

    Поддерживает распространённые варианты структур:
    - Корневой словарь с ключами channels|items|results|data -> список словарей
    - Вложенные словари, где есть ключи выше
    - Имя id: предпочитаем our_id, затем id
    Возвращает список строковых id.
    """
    ids: List[str] = []

    def scan_list(lst: List[Any]) -> None:
        for it in lst:
            if isinstance(it, dict):
                # Приоритет our_id
                if "our_id" in it and it["our_id"] is not None:
                    ids.append(str(it["our_id"]))
                elif "id" in it and it["id"] is not None:
                    ids.append(str(it["id"]))
                # Иногда каналы лежат вложенно
                for k, v in it.items():
                    if isinstance(v, list):
                        scan_list(v)
                    elif isinstance(v, dict):
                        scan_dict(v)

    def scan_dict(d: Dict[str, Any]) -> None:
        # Популярные ключи
        for key in ("channels", "items", "results", "data"):
            v = d.get(key)
            if isinstance(v, list):
                scan_list(v)
        # Общий обход
        for v in d.values():
            if isinstance(v, list):
                scan_list(v)
            elif isinstance(v, dict):
                scan_dict(v)

    if isinstance(obj, list):
        scan_list(obj)
    elif isinstance(obj, dict):
        scan_dict(obj)

    # Уникализируем порядок
    seen = set()
    uniq: List[str] = []
    for x in ids:
        if x not in seen:
            uniq.append(x)
            seen.add(x)
    return uniq


@app.command()
def fetch_epg_for_playlist(
    limit: Optional[int] = typer.Option(None, help="Ограничить количество каналов для запроса"),
    grouping: int = typer.Option(2, help="Параметр grouping для EPG-запроса"),
) -> None:
    """Пройти по каналам из data/raw_playlist.json, запросить EPG и
    сохранить каждый канал в data/epg_channels/{id}.json.

    Формат файла: {"our_id": "<id>", "epg": [...]}.
    """
    cfg = load_config()
    setup_logging(cfg.log_level)

    if not RAW_PLAYLIST_PATH.exists():
        print(f"[yellow]{RAW_PLAYLIST_PATH} не найден. Сначала выполните fetch-playlist-cmd[/yellow]")
        raise typer.Exit(code=1)

    try:
        playlist_obj: Any = json.loads(RAW_PLAYLIST_PATH.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[red]Не удалось прочитать {RAW_PLAYLIST_PATH}: {e}[/red]")
        raise typer.Exit(code=1)

    channel_ids = _extract_channel_ids_from_playlist(playlist_obj)
    if not channel_ids:
        print("[red]Не удалось извлечь список каналов (our_id/id) из плейлиста[/red]")
        raise typer.Exit(code=1)

    if limit is not None:
        channel_ids = channel_ids[:limit]

    session = create_session(cfg)
    saved = 0
    for cid in track(channel_ids, description="Загрузка EPG по каналам"):
        epg_items = fetch_epg_for_channel(cfg, session, cid, grouping=grouping)
        out = {"our_id": cid, "epg": epg_items}
        out_path = EPG_CHANNELS_DIR / f"{cid}.json"
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        saved += 1

    print(f"[green]Сохранено[/green] EPG файлов: {saved} в {EPG_CHANNELS_DIR}")


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
    print(f"[green]Сохранено[/green] отфильтрованных фильмов: {len(movies)} в {MOVIES_PATH}")


@app.command()
def filter_epg_movies(
    skip_empty: bool = typer.Option(True, help="Не сохранять файлы, где после фильтрации нет фильмов"),
) -> None:
    """Отфильтровать EPG каждого канала в data/epg_channels/ и сохранить только фильмы.

    - Критерий: category == "Х/ф" (как в filter_movies_by_category)
    - Результат: data/epg_channels_filtered/{id}.movies.json
      Формат: {"our_id": "<id>", "epg": [только фильмы]}
    """
    cfg = load_config()
    setup_logging(cfg.log_level)

    if not EPG_CHANNELS_DIR.exists():
        print(f"[yellow]{EPG_CHANNELS_DIR} не найден. Сначала выполните fetch-epg-for-playlist[/yellow]")
        raise typer.Exit(code=1)

    files = sorted([p for p in EPG_CHANNELS_DIR.glob("*.json") if p.is_file()])
    if not files:
        print(f"[yellow]Нет файлов в {EPG_CHANNELS_DIR}[/yellow]")
        raise typer.Exit(code=1)

    saved = 0
    aggregated: List[Dict[str, Any]] = []
    processed = 0
    for path in track(files, description="Фильтрация EPG по фильмам"):
        processed += 1
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[red]Ошибка чтения {path.name}: {e}[/red]")
            continue

        our_id = str(obj.get("our_id") or path.stem)
        items = obj.get("epg")
        if not isinstance(items, list):
            # Пытаемся найти альтернативные ключи
            for k in ("items", "results", "data"):
                v = obj.get(k)
                if isinstance(v, list):
                    items = v
                    break

        if not isinstance(items, list):
            print(f"[yellow]{path.name}: пропуск (не найден список EPG)[/yellow]")
            continue

        # Разворачиваем суточные группы, если формат: [{"date":..., "title":..., "data": [...]}]
        flat_items: List[Dict[str, Any]] = []
        for elem in items:
            if isinstance(elem, dict) and isinstance(elem.get("data"), list):
                for sub in elem["data"]:
                    if isinstance(sub, dict):
                        flat_items.append(sub)
            elif isinstance(elem, dict):
                flat_items.append(elem)

        # Строгая фильтрация: только элементы, где в category есть "Х/ф"
        movies = filter_movies_by_category(flat_items)
        if not movies:
            # Не создаём файл; если существовал ранее — удаляем
            out_path = EPG_FILTERED_DIR / f"{our_id}.movies.json"
            if out_path.exists():
                try:
                    out_path.unlink()
                except Exception:
                    pass
            if skip_empty:
                continue

        out = {"our_id": our_id, "epg": movies}
        out_path = EPG_FILTERED_DIR / f"{our_id}.movies.json"
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        saved += 1
        # Агрегируем с добавлением идентификатора канала внутрь каждого элемента
        for m in movies:
            if isinstance(m, dict):
                m_with_id = dict(m)
                m_with_id.setdefault("our_id", our_id)
                aggregated.append(m_with_id)

    # Сохраняем агрегированный список фильмов из EPG
    EPG_MOVIES_PATH.write_text(json.dumps(aggregated, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[green]Готово[/green]: обработано {processed} файлов, сохранено {saved} в {EPG_FILTERED_DIR}; агрегировано {len(aggregated)} фильмов в {EPG_MOVIES_PATH}")


@app.command()
def filter_epg_cartoons(
    skip_empty: bool = typer.Option(True, help="Не сохранять файлы, где после фильтрации нет мультфильмов"),
) -> None:
    """Отфильтровать EPG каждого канала и сохранить только мультфильмы (категория содержит "М/ф").

    - Результат: data/epg_channels_cartoons/{id}.cartoons.json
      Формат: {"our_id": "<id>", "epg": [только мультфильмы]}
    - Агрегация: data/epg_cartoons.json
    """
    cfg = load_config()
    setup_logging(cfg.log_level)

    if not EPG_CHANNELS_DIR.exists():
        print(f"[yellow]{EPG_CHANNELS_DIR} не найден. Сначала выполните fetch-epg-for-playlist[/yellow]")
        raise typer.Exit(code=1)

    files = sorted([p for p in EPG_CHANNELS_DIR.glob("*.json") if p.is_file()])
    if not files:
        print(f"[yellow]Нет файлов в {EPG_CHANNELS_DIR}[/yellow]")
        raise typer.Exit(code=1)

    saved = 0
    aggregated: List[Dict[str, Any]] = []
    processed = 0
    for path in track(files, description="Фильтрация EPG по мультфильмам"):
        processed += 1
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[red]Ошибка чтения {path.name}: {e}[/red]")
            continue

        our_id = str(obj.get("our_id") or path.stem)
        items = obj.get("epg")
        if not isinstance(items, list):
            for k in ("items", "results", "data"):
                v = obj.get(k)
                if isinstance(v, list):
                    items = v
                    break

        if not isinstance(items, list):
            print(f"[yellow]{path.name}: пропуск (не найден список EPG)[/yellow]")
            continue

        # Разворачиваем суточные группы, если формат: [{"date":..., "title":..., "data": [...]}]
        flat_items: List[Dict[str, Any]] = []
        for elem in items:
            if isinstance(elem, dict) and isinstance(elem.get("data"), list):
                for sub in elem["data"]:
                    if isinstance(sub, dict):
                        flat_items.append(sub)
            elif isinstance(elem, dict):
                flat_items.append(elem)

        cartoons = filter_cartoons_by_category(flat_items)
        if not cartoons:
            out_path = EPG_CARTOONS_DIR / f"{our_id}.cartoons.json"
            if out_path.exists():
                try:
                    out_path.unlink()
                except Exception:
                    pass
            if skip_empty:
                continue

        out = {"our_id": our_id, "epg": cartoons}
        out_path = EPG_CARTOONS_DIR / f"{our_id}.cartoons.json"
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
        saved += 1
        for m in cartoons:
            if isinstance(m, dict):
                m_with_id = dict(m)
                m_with_id.setdefault("our_id", our_id)
                aggregated.append(m_with_id)

    EPG_CARTOONS_PATH.write_text(json.dumps(aggregated, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[green]Готово[/green]: обработано {processed} файлов, сохранено {saved} в {EPG_CARTOONS_DIR}; агрегировано {len(aggregated)} элементов в {EPG_CARTOONS_PATH}")

def _enrich(limit: Optional[int] = None) -> None:
    """Внутренняя реализация обогащения фильмов."""
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
    for item in track(movies, description="Обогащение (TMDB->КиноПоиск) и загрузка постеров"):
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
        # 1) Пытаемся получить данные из TMDB, 2) если нет — из КиноПоиска
        tmdb_info = tmdb.get_movie_info(title)
        info = tmdb_info if tmdb_info else kp.get_movie_info(title)

        # Подбор URL постера: сначала TMDB, затем КиноПоиск, затем превью из EPG
        candidate_urls: List[Dict[str, Any]] = []  # {url, source}
        if isinstance(info, dict):
            # Если инфо из TMDB и содержит постер — приоритет
            if info.get("source") == "tmdb":
                pu = info.get("poster_url")
                if isinstance(pu, str) and pu.startswith("http"):
                    candidate_urls.append({"url": pu, "source": "tmdb"})
            # Fallback: для КиноПоиска, если указан постер
            pu_kp = info.get("poster_url")
            if isinstance(pu_kp, str) and pu_kp.startswith("http"):
                candidate_urls.append({"url": pu_kp, "source": "kinopoisk"})
        # Дополнительный fallback: отдельный запрос к TMDB только за постером (если не нашли выше)
        if tmdb.is_enabled():
            year_hint = None
            if isinstance(info, dict) and isinstance(info.get("year"), int):
                year_hint = info.get("year")
            tmdb_url = tmdb.get_poster_url(title, year=year_hint)
            if isinstance(tmdb_url, str) and tmdb_url.startswith("http"):
                candidate_urls.append({"url": tmdb_url, "source": "tmdb"})
        # Последний вариант — превью из EPG
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
def enrich(limit: Optional[int] = typer.Option(None, help="Ограничить количество фильмов для обогащения")) -> None:
    """CLI-обёртка над _enrich."""
    _enrich(limit)


@app.command()
def run_all() -> None:
    """Полный цикл: загрузка EPG, фильтрация фильмов, обогащение."""
    fetch_epg_cmd()
    filter_movies_cmd()
    _enrich()


if __name__ == "__main__":
    app()
