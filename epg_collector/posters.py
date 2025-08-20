from __future__ import annotations

import re
import hashlib
from pathlib import Path
from typing import Optional

import requests


IMAGE_CT_TO_EXT = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}

MIN_VALID_BYTES = 10240  # минимальный размер валидного изображения (~10KB), чтобы отсечь слишком маленькие превью


def _looks_like_image_magic(data: bytes) -> bool:
    """Простейшая проверка магических байт JPG/PNG/WEBP."""
    if not data or len(data) < 8:
        return False
    # JPEG: FF D8
    if data[:2] == b"\xFF\xD8":
        return True
    # PNG: 89 50 4E 47 0D 0A 1A 0A
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        return True
    # WEBP: RIFF....WEBP
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True
    return False


def is_valid_image_file(path: Path) -> bool:
    """Проверяет, что локальный файл действительно выглядит как изображение и не слишком мал.

    Условия:
    - файл существует и это файл
    - размер >= MIN_VALID_BYTES
    - первые байты соответствуют сигнатурам JPG/PNG/WEBP
    """
    try:
        if not (path and path.exists() and path.is_file()):
            return False
        size = path.stat().st_size
        if size < MIN_VALID_BYTES:
            return False
        with open(path, "rb") as f:
            head = f.read(16)
        return _looks_like_image_magic(head)
    except Exception:
        return False


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9\-_.]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-._")
    return value or "item"


def _guess_ext(url: str, content_type: Optional[str]) -> str:
    if content_type and content_type.lower() in IMAGE_CT_TO_EXT:
        return IMAGE_CT_TO_EXT[content_type.lower()]
    # try from url
    m = re.search(r"\.(jpg|jpeg|png|webp)(?:\?|$)", url, flags=re.IGNORECASE)
    if m:
        ext = m.group(1).lower()
        return ".jpg" if ext == "jpeg" else f".{ext}"
    return ".jpg"


def download_poster(session: requests.Session, url: str, posters_dir: Path, *, title: str, epg_id: Optional[int]) -> Optional[str]:
    """Скачать постер и вернуть относительный путь (str) или None при ошибке.

    Имя файла строится из epg_id + slug(title). Повторные скачивания избегаются, если файл уже существует.
    """
    try:
        posters_dir.mkdir(parents=True, exist_ok=True)
        slug = _slugify(title)
        id_part = str(epg_id) if epg_id is not None else hashlib.sha1(title.encode("utf-8")).hexdigest()[:8]

        # Если файл уже существует с любой известной графической экстеншн — вернём его без сети
        base = f"{id_part}-{slug}"
        for ext in (".jpg", ".png", ".webp"):
            existing = posters_dir / f"{base}{ext}"
            if existing.exists():
                if is_valid_image_file(existing):
                    return str(existing.as_posix())
                # Удалим повреждённый/слишком маленький файл и попробуем скачать заново
                try:
                    existing.unlink(missing_ok=True)
                except Exception:
                    pass

        # Предварительный HEAD для типа контента может блокироваться, сразу GET c stream
        resp = session.get(url, stream=True)
        resp.raise_for_status()
        content_type = resp.headers.get("Content-Type")
        if not (isinstance(content_type, str) and content_type.lower().startswith("image/")):
            # Некоторые CDN возвращают text/html или application/json при ошибке
            return None
        ext = _guess_ext(url, content_type)

        filename = f"{base}{ext}"
        path = posters_dir / filename
        if not path.exists():
            total = 0
            first_chunk: Optional[bytes] = None
            with open(path, "wb") as f:
                for chunk in resp.iter_content(chunk_size=64 * 1024):
                    if not chunk:
                        continue
                    if first_chunk is None:
                        first_chunk = bytes(chunk)
                    f.write(chunk)
                    total += len(chunk)

            # Валидация: магические байты и минимальный размер
            if first_chunk is None or not _looks_like_image_magic(first_chunk) or total < MIN_VALID_BYTES:
                try:
                    path.unlink(missing_ok=True)
                finally:
                    return None
        # Возвращаем относительный путь в unix-стиле для переносимости
        return str(path.as_posix())
    except Exception:
        return None
