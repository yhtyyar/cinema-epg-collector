from __future__ import annotations

import logging
from typing import Any, Dict, List
import json

from .config import Config
from .epg_manager import EPGManager

logger = logging.getLogger(__name__)


def fetch_epg(cfg: Config, session) -> List[Dict[str, Any]]:
    """Запрашивает EPG с IPTV API и возвращает список элементов EPG.

    Ожидается, что ответ может содержать ключ `epg` или быть списком.
    """
    logger.info("Fetching EPG from %s", cfg.iptv_base_url)
    resp = session.get(
        cfg.iptv_base_url,
        params=cfg.iptv_params,
        headers=cfg.iptv_headers,
    )
    resp.raise_for_status()
    # Принудительно используем UTF-8 (некоторые провайдеры выставляют неверную кодировку)
    try:
        resp.encoding = "utf-8"
    except Exception:
        pass
    # Надёжный парсинг JSON: сначала пытаемся обычным способом, затем — декодируем байты
    try:
        data = resp.json()
    except ValueError:
        raw = resp.content or b""
        last_err = None
        for enc in ("utf-8", "cp1251", "latin-1"):
            try:
                data = json.loads(raw.decode(enc))
                logger.info("EPG JSON decoded with %s", enc)
                break
            except Exception as e:
                last_err = e
                data = None
        if data is None:
            text_sample = (resp.text or "")[:200]
            logger.warning("EPG response is not valid JSON after decode attempts. Sample: %r; last_err=%s", text_sample, last_err)
            return []

    if isinstance(data, dict):
        epg = data.get("epg")
        if isinstance(epg, list):
            logger.info("EPG items: %d", len(epg))
            return epg
        # Если структура иная, но сам словарь — это элемент EPG
        if all(k in data for k in ("title", "timestart", "timestop")):
            return [data]
        # Попробуем найти список внутри словаря
        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                logger.info("EPG items (nested): %d", len(v))
                return v
        logger.warning("Не удалось определить список EPG в ответе, возвращаю пустой список")
        return []

    if isinstance(data, list):
        logger.info("EPG items (root list): %d", len(data))
        return data

    logger.warning("Unexpected EPG response type: %s", type(data))
    return []
