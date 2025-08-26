from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
import json

from .config import Config

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


def fetch_epg_for_channel(
    cfg: Config,
    session,
    channel_id: Any,
    grouping: Optional[int] = None,
    extra_params: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """Запрашивает EPG для конкретного канала (id) с возможностью переопределить grouping и добавить параметры.

    Параметры берутся из cfg.iptv_params с подстановкой id=channel_id.
    По умолчанию используются заголовки cfg.iptv_headers.
    Возвращает список элементов EPG.
    """
    params: Dict[str, Any] = dict(cfg.iptv_params)
    params["id"] = str(channel_id)
    if grouping is not None:
        params["grouping"] = str(grouping)
    if extra_params:
        for k, v in extra_params.items():
            if v is not None:
                params[str(k)] = str(v)

    logger.info("Fetching EPG for channel id=%s from %s", channel_id, cfg.iptv_base_url)
    resp = session.get(
        cfg.iptv_base_url,
        params=params,
        headers=cfg.iptv_headers,
    )
    resp.raise_for_status()

    try:
        resp.encoding = "utf-8"
    except Exception:
        pass

    try:
        data = resp.json()
    except ValueError:
        raw = resp.content or b""
        last_err = None
        for enc in ("utf-8", "cp1251", "latin-1"):
            try:
                data = json.loads(raw.decode(enc))
                logger.info("EPG JSON decoded with %s (channel %s)", enc, channel_id)
                break
            except Exception as e:
                last_err = e
                data = None
        if data is None:
            text_sample = (resp.text or "")[:200]
            logger.warning(
                "EPG response is not valid JSON after decode attempts for channel %s. Sample: %r; last_err=%s",
                channel_id,
                text_sample,
                last_err,
            )
            return []

    if isinstance(data, dict):
        epg = data.get("epg")
        if isinstance(epg, list):
            logger.info("EPG items for channel %s: %d", channel_id, len(epg))
            return epg
        if all(k in data for k in ("title", "timestart", "timestop")):
            return [data]
        for v in data.values():
            if isinstance(v, list) and v and isinstance(v[0], dict):
                logger.info("EPG items (nested) for channel %s: %d", channel_id, len(v))
                return v
        logger.warning("Не удалось определить список EPG в ответе (channel %s), возвращаю пустой список", channel_id)
        return []

    if isinstance(data, list):
        logger.info("EPG items (root list) for channel %s: %d", channel_id, len(data))
        return data

    logger.warning("Unexpected EPG response type for channel %s: %s", channel_id, type(data))
    return []
