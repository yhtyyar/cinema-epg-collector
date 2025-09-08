import requests
import json
from datetime import datetime
import re
from typing import Any, Iterable, Dict, List, Union, Set

# Заголовки из curl-запроса
HEADERS = {
    "Host": "pl.iptv2021.com",
    "User-Agent": "Mozilla/5.0 (Linux; Android 11; SM-A127F Build/RP1A.200720.012; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/138.0.7204.179 Mobile Safari/537.36",
    "x-lhd-agent": "{\"generation\":2,\"sdk\":30,\"version_name\":\"5.7.12\",\"version_code\":851,\"platform\":\"android\",\"device_id\":\"5dda2a6f7dcbe35f\",\"name\":\"samsung+SM-A127F\",\"app\":\"com.infolink.limeiptv\"}",
    "x-token": "0a17dbac5958fbf1d31a351386802afe"
}

# URL запроса
URL = "https://pl.iptv2021.com/api/v4/epg?id=126&tz=3&epg_from=-7&epg_limit=14&grouping=1&region=0&lang=ru"

# Ключевые слова для определения фильмов
MOVIE_KEYWORDS: Set[str] = {"х/ф", "х-ф", "фильм", "кино", "movie", "film"}

def _to_list(val: Any) -> List[Any]:
    if val is None:
        return []
    if isinstance(val, list):
        return val
    if isinstance(val, (str, int, float)):
        return [val]
    return [val]

def _norm(s: Union[str, None]) -> str:
    return s.strip().lower() if isinstance(s, str) else ""

def extract_categories(item: Dict[str, Any]) -> List[str]:
    """Извлекает категории/жанры из разных возможных полей и вложенностей."""
    candidates = ["category", "categories", "genre", "genres", "tvg_genre", "tvg-category"]
    cats: List[str] = []
    for k in candidates:
        if k in item:
            v = item[k]
            for el in _to_list(v):
                if isinstance(el, str):
                    cats.append(_norm(el))

    # Возможные вложенные контейнеры с метаданными
    for k in ("info", "ext", "meta"):
        sub = item.get(k)
        if isinstance(sub, dict):
            cats.extend(extract_categories(sub))

    return cats

def title_contains_movie(item: Dict[str, Any]) -> bool:
    title = item.get("title") or item.get("name") or item.get("program") or item.get("t")
    if not isinstance(title, str):
        return False
    t = _norm(title)
    # Варианты записи: "Х/ф", "Х - ф", "Х/ Ф" и т.п.
    if re.search(r"\bх\s*[/\-]\s*ф\b", t):
        return True
    return any(kw in t for kw in MOVIE_KEYWORDS)

def looks_like_program(item: Dict[str, Any]) -> bool:
    if not isinstance(item, dict):
        return False
    has_title = any(isinstance(item.get(k), str) for k in ("title", "name", "program", "t"))
    has_time = any(k in item for k in ("start", "start_time", "time", "begin", "from", "s"))
    return has_title or has_time

def flatten_programs(obj: Any) -> Iterable[Dict[str, Any]]:
    """Рекурсивно обходит любую структуру и извлекает элементы, похожие на EPG-записи."""
    if isinstance(obj, dict):
        if looks_like_program(obj):
            yield obj

        # Часто встречающиеся контейнеры
        for key in ("epg", "programs", "list", "items", "events", "data", "rows", "result", "values", "channel", "channels"):
            if key in obj:
                yield from flatten_programs(obj[key])

        # Фолбэк: обойти все словари/списки внутри
        for v in obj.values():
            if isinstance(v, (list, dict)):
                yield from flatten_programs(v)

    elif isinstance(obj, list):
        for el in obj:
            yield from flatten_programs(el)

def is_movie(item: Dict[str, Any]) -> bool:
    cats = set(extract_categories(item))
    if any(any(kw in c for kw in MOVIE_KEYWORDS) for c in cats):
        return True
    return title_contains_movie(item)

def unique_key(item: Dict[str, Any]) -> str:
    title = _norm(item.get("title") or item.get("name") or "")
    start = str(item.get("start") or item.get("time") or item.get("begin") or item.get("from") or "")
    return f"{title}|{start}"

# Основная функция
def main():
    try:
        print("Отправка запроса...")
        response = requests.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()  # Проверка на ошибки HTTP

        print("Получение данных...")
        data = response.json()

        print("Анализ структуры и извлечение программ...")
        programs = list(flatten_programs(data))
        print(f"Найдено программ/элементов: {len(programs)}")

        print("Фильтрация фильмов...")
        seen: Set[str] = set()
        movies: List[Dict[str, Any]] = []
        for p in programs:
            if is_movie(p):
                key = unique_key(p)
                if key not in seen:
                    seen.add(key)
                    movies.append(p)

        # Сохранение в файл
        output_file = "filtered_result.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(movies, f, ensure_ascii=False, indent=4)

        print(f"Сохранено {len(movies)} фильмов в файл: {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
    except json.JSONDecodeError as e:
        print(f"Ошибка при парсинге JSON: {e}")
    except Exception as e:
        print(f"Неизвестная ошибка: {e}")

if __name__ == "__main__":
    main()