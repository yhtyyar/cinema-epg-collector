from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple


class TTLCache:
    """Простой in-memory TTL кэш для объектов.

    Не предназначен для высоконагруженных сценариев, но достаточен для локального API.
    """

    def __init__(self, ttl_seconds: int = 300):
        self._ttl = ttl_seconds
        self._store: Dict[str, Tuple[float, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        now = time.time()
        item = self._store.get(key)
        if not item:
            return None
        expires_at, value = item
        if expires_at < now:
            # expired
            self._store.pop(key, None)
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        expires_at = time.time() + self._ttl
        self._store[key] = (expires_at, value)

    def clear(self) -> None:
        self._store.clear()

    def set_ttl(self, ttl_seconds: int) -> None:
        self._ttl = ttl_seconds
        # Не пересчитываем текущие элементы; новые будут с новым TTL
