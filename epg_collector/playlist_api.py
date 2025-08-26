from __future__ import annotations

import json
import logging
from typing import Any, Dict

from .config import Config

logger = logging.getLogger(__name__)


def fetch_playlist(cfg: Config, session) -> Dict[str, Any]:
    """Запрашивает Playlist API (POST form-urlencoded) и возвращает распарсенный JSON.

    Возвращаем словарь (или пустой словарь при ошибке). Структура ответа зависит
    от поставщика и может включать категории, каналы и др.
    """
    logger.info("Fetching Playlist from %s", cfg.playlist_base_url)

    resp = session.post(
        cfg.playlist_base_url,
        params=cfg.playlist_params,
        headers=cfg.playlist_headers,
        data=cfg.playlist_form,
    )
    resp.raise_for_status()

    # Принудительно используем UTF-8 (иногда серверы выставляют неверную кодировку)
    try:
        resp.encoding = "utf-8"
    except Exception:
        pass

    # Надёжный парсинг JSON: сначала обычным способом, затем через декодирование байтов
    try:
        data = resp.json()
        if isinstance(data, dict):
            logger.info("Playlist keys: %s", ", ".join(list(data.keys())[:10]))
        return data if isinstance(data, dict) else {"data": data}
    except ValueError:
        raw = resp.content or b""
        last_err = None
        for enc in ("utf-8", "cp1251", "latin-1"):
            try:
                data = json.loads(raw.decode(enc))
                logger.info("Playlist JSON decoded with %s", enc)
                return data if isinstance(data, dict) else {"data": data}
            except Exception as e:
                last_err = e
        text_sample = (resp.text or "")[:200]
        logger.warning(
            "Playlist response is not valid JSON after decode attempts. Sample: %r; last_err=%s",
            text_sample,
            last_err,
        )
        return {}
