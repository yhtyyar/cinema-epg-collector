from __future__ import annotations

from typing import Any, Dict, Iterable, List


def filter_movies_by_category(items: Iterable[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Фильтрует элементы, у которых поле `category` содержит значение "Х/ф".

    Допускаются варианты, где `category` — список строк или одна строка.
    """
    result: List[Dict[str, Any]] = []
    for item in items:
        cat = item.get("category")
        if isinstance(cat, list) and any(isinstance(c, str) and c.strip().lower() == "х/ф" for c in cat):
            result.append(item)
        elif isinstance(cat, str) and cat.strip().lower() == "х/ф":
            result.append(item)
    return result
