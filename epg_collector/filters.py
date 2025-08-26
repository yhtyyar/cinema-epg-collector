from __future__ import annotations

from typing import Any, Dict, Iterable, List


def filter_movies_by_category(items: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Фильтрует элементы, у которых поле `category` содержит значение "Х/ф".

    Допускаются варианты, где `category` — список строк или одна строка.
    """
    result: List[Dict[str, Any]] = []
    anti_series_kw = [
        "сезон",
        "серия",
        "эпизод",
        "сер.",
        "series",
        "episode",
        "season",
    ]
    anti_series_kw = [s.casefold() for s in anti_series_kw]
    for item in items:
        cat = item.get("category")
        if isinstance(cat, list) and any(isinstance(c, str) and c.strip().lower() == "х/ф" for c in cat):
            result.append(item)
        elif isinstance(cat, str) and cat.strip().lower() == "х/ф":
            result.append(item)
    return result


def filter_cartoons_by_category(items: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Фильтрует элементы, у которых поле `category` содержит значение "М/ф".

    Допускаются варианты, где `category` — список строк или одна строка.
    """
    result: List[Dict[str, Any]] = []
    for item in items:
        cat = item.get("category")
        if isinstance(cat, list) and any(isinstance(c, str) and c.strip().lower() == "м/ф" for c in cat):
            result.append(item)
        elif isinstance(cat, str) and cat.strip().lower() == "м/ф":
            result.append(item)
    return result


def filter_movies_epg(
    items: Iterable[Dict[str, Any]],
    keywords: List[str] | None = None,
    min_duration_minutes: int | None = None,
) -> List[Dict[str, Any]]:
    """Фильтрует элементы EPG, относящиеся к фильмам.

    Логика:
    1) Смотрим в поля категорий: category/categories/genre/genres/tags/program_type/type
       - Если это список строк — ищем совпадение/вхождение по ключевым словам
       - Если это строка — аналогично
    2) Если по категориям не найдено, проверяем эвристику по названию/описанию:
       - title/name + description/desc/short_desc
       - Ищем ключевые слова (например, «Х/ф», «фильм», «кино», «feature film», «movie»)

    По умолчанию ключевые слова: ["Х/ф", "х/ф", "Художественный фильм", "фильм", "кино", "movie", "feature film"].
    Сопоставление без учета регистра и диакритики (через .casefold()).
    """
    if keywords is None:
        keywords = [
            "Х/ф",
            "х/ф",
            "Художественный фильм",
            "фильм",
            "кино",
            "movie",
            "feature film",
        ]

    kw = [k.casefold() for k in keywords if isinstance(k, str) and k.strip()]
    if not kw:
        return []

    def text_has_movie_markers(text: str) -> bool:
        t = text.casefold()
        return any(k in t for k in kw)

    result: List[Dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue

        # 1) Категории/жанры/теги
        category_keys = (
            "category",
            "categories",
            "genre",
            "genres",
            "tags",
            "program_type",
            "type",
        )
        matched = False
        for key in category_keys:
            v = item.get(key)
            if isinstance(v, list):
                texts = [str(x) for x in v if isinstance(x, (str, int, float))]
                if any(text_has_movie_markers(s) for s in texts):
                    matched = True
                    break
            elif isinstance(v, (str, int, float)):
                if text_has_movie_markers(str(v)):
                    matched = True
                    break

        # 2) Эвристика по названию/описанию
        if not matched:
            title = item.get("title") or item.get("name") or ""
            desc = (
                item.get("description")
                or item.get("desc")
                or item.get("short_desc")
                or ""
            )
            if isinstance(title, str) and text_has_movie_markers(title):
                matched = True
            elif isinstance(desc, str) and text_has_movie_markers(desc):
                matched = True

        # 3) Эвристика по длительности (если не нашли по категориям/тексту)
        if not matched and min_duration_minutes is not None:
            ts = item.get("timestart")
            te = item.get("timestop")
            try:
                ts_i = int(ts) if ts is not None else None
                te_i = int(te) if te is not None else None
                if ts_i and te_i and te_i > ts_i:
                    dur_min = (te_i - ts_i) // 60
                    if dur_min >= int(min_duration_minutes):
                        # Исключим явные сериалы по названию
                        t = str(title).casefold()
                        if not any(x in t for x in anti_series_kw):
                            matched = True
            except Exception:
                pass

        if matched:
            result.append(item)

    return result
