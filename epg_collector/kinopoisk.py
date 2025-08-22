from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from .config import Config

logger = logging.getLogger(__name__)


class KinoPoiskClient:
    """Клиент для получения информации о фильме по названию.

    При наличии API-ключа использует https://api.kinopoisk.dev.
    Иначе пытается выполнить веб-поиск на https://www.kinopoisk.ru (best-effort, может блокироваться).
    Результаты кэшируются в файловой системе по названию фильма.
    """

    def __init__(self, cfg: Config, session):
        self.cfg = cfg
        self.session = session
        self.cache_dir = Path("cache/kinopoisk")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, title: str) -> Path:
        key = hashlib.sha1(title.strip().lower().encode("utf-8")).hexdigest()
        return self.cache_dir / f"{key}.json"

    def _load_cache(self, title: str) -> Optional[Dict[str, Any]]:
        path = self._cache_path(title)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                # Не используем кэш, если там явно антибот или битая кодировка
                name = (data or {}).get("name")
                if isinstance(name, str) and self._is_bad_name(name):
                    logger.info("Kinopoisk cache contains invalid name for '%s', ignoring cache", title)
                    return None
                return data
            except Exception:
                return None
        return None

    def _save_cache(self, title: str, data: Dict[str, Any]) -> None:
        path = self._cache_path(title)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def get_movie_info(self, title: str) -> Optional[Dict[str, Any]]:
        cached = self._load_cache(title)
        if cached is not None:
            logger.debug("Kinopoisk cache hit for '%s'", title)
            return cached

        data: Optional[Dict[str, Any]] = None
        if self.cfg.kinopoisk_api_key:
            data = self._query_api(title)
        if data is None:
            data = self._scrape_web(title)

        # Финальная валидация + починка mojibake
        if isinstance(data, dict):
            nm = data.get("name")
            if isinstance(nm, str):
                data["name"] = self._fix_mojibake(nm)
            if self._is_bad_name(data.get("name")):
                logger.info("Kinopoisk: dropping invalid result for '%s' (robot or bad name)", title)
                data = None

        if data is not None:
            self._save_cache(title, data)
        return data

    # --- API mode ---
    def _query_api(self, title: str) -> Optional[Dict[str, Any]]:
        base = self.cfg.kinopoisk_base_url.rstrip("/")
        url = f"{base}/movie/search"
        headers = {"X-API-KEY": self.cfg.kinopoisk_api_key}
        params = {"query": title, "limit": 1}
        try:
            resp = self.session.get(url, headers=headers, params=params)
            if resp.status_code == 401:
                logger.error("Kinopoisk API unauthorized. Check KINOPOISK_API_KEY")
                return None
            resp.raise_for_status()
            js = resp.json()
            docs = js.get("docs") if isinstance(js, dict) else None
            if not docs:
                logger.info("Kinopoisk API: no results for '%s'", title)
                return None
            m = docs[0]
            return {
                "source": "api",
                "kp_id": m.get("id"),
                "name": m.get("name") or m.get("alternativeName"),
                "year": m.get("year"),
                "rating_kp": (m.get("rating") or {}).get("kp"),
                "rating_imdb": (m.get("rating") or {}).get("imdb"),
                "genres": [g.get("name") for g in (m.get("genres") or []) if isinstance(g, dict)],
                "countries": [c.get("name") for c in (m.get("countries") or []) if isinstance(c, dict)],
                "poster_url": (m.get("poster") or {}).get("url"),
                "url": f"https://www.kinopoisk.ru/film/{m.get('id')}/" if m.get("id") else None,
            }
        except Exception as e:
            logger.exception("Kinopoisk API error for '%s': %s", title, e)
            return None

    # --- Web scraping fallback ---
    def _scrape_web(self, title: str) -> Optional[Dict[str, Any]]:
        try:
            q = quote_plus(title)
            search_url = f"https://www.kinopoisk.ru/index.php?kp_query={q}"
            r = self.session.get(
                search_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Connection": "keep-alive",
                },
                expire_after=0,
            )
            r.raise_for_status()
            # Выставим явную кодировку, если не определена
            if not r.encoding:
                r.encoding = r.apparent_encoding or "utf-8"
            soup = BeautifulSoup(r.text, "lxml")

            if self._looks_like_robot_page(soup):
                logger.warning("Kinopoisk search blocked by anti-bot for '%s'", title)
                return None

            # Простой парс: взять первую ссылку на фильм
            link = soup.select_one(".most_wanted .element.most_wanted .info a[href^='/film/'], a[href^='/film/']")
            if not link or not link.get("href"):
                logger.info("Kinopoisk search: no film link for '%s'", title)
                return None
            href = link["href"]
            film_url = f"https://www.kinopoisk.ru{href}" if href.startswith("/") else href

            r2 = self.session.get(
                film_url,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
                    "Referer": "https://www.kinopoisk.ru/",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
                    "Connection": "keep-alive",
                },
                expire_after=0,
            )
            r2.raise_for_status()
            if not r2.encoding:
                r2.encoding = r2.apparent_encoding or "utf-8"
            soup2 = BeautifulSoup(r2.text, "lxml")

            if self._looks_like_robot_page(soup2):
                logger.warning("Kinopoisk film page blocked by anti-bot for '%s'", title)
                return None

            # Пробуем вытащить базовые поля (best effort)
            name_tag = soup2.select_one("h1[data-tid]") or soup2.select_one("h1")
            raw_name = name_tag.get_text(strip=True) if name_tag else title
            name = self._fix_mojibake(raw_name)

            rating_tag = soup2.select_one("span.film-rating-value, span.rating__value")
            rating_kp = rating_tag.get_text(strip=True) if rating_tag else None

            # Год
            year_tag = soup2.find(string=lambda s: s and "год" in s.lower())
            year = None
            if year_tag and year_tag.parent:
                try:
                    year = int("".join(filter(str.isdigit, year_tag.parent.get_text())))
                except Exception:
                    year = None

            # Постер: сначала og:image, затем типовые селекторы
            poster_url = None
            og_img = soup2.select_one('meta[property="og:image"]')
            if og_img and og_img.get("content"):
                poster_url = og_img.get("content")
            if not poster_url:
                img_tag = soup2.select_one("img.film-poster, img.poster, img[loading][src]")
                if img_tag and img_tag.get("src"):
                    poster_url = img_tag["src"]

            result = {
                "source": "web",
                "kp_id": None,
                "name": name,
                "year": year,
                "rating_kp": rating_kp,
                "rating_imdb": None,
                "genres": None,
                "countries": None,
                "poster_url": poster_url,
                "url": film_url,
            }
            if self._is_bad_name(result.get("name")):
                logger.info("Kinopoisk scraping produced invalid name for '%s' (robot/bad encoding)", title)
                return None
            return result
        except Exception as e:
            logger.exception("Kinopoisk scraping error for '%s': %s", title, e)
            return None

    # --- Helpers ---
    def _looks_like_robot_page(self, soup: BeautifulSoup) -> bool:
        try:
            text = soup.get_text(" ", strip=True)
            if not text:
                return False
            t = text.lower()
            return (
                ("подтвердите" in t and "не робот" in t)
                or "captcha" in t
                or "robot" in t and "verify" in t
            )
        except Exception:
            return False

    def _is_bad_name(self, name: Optional[str]) -> bool:
        if not isinstance(name, str) or not name.strip():
            return True
        s = name.strip()
        # Известная строка антибота и типичный mojibake-паттерн
        if "Подтвердите, что запросы отправляли вы, а не робот" in s:
            return True
        if "Ð" in s or "Ñ" in s:
            # вероятная неправильная кодировка
            try:
                fixed = s.encode("latin-1", errors="ignore").decode("utf-8", errors="ignore")
                if fixed and fixed != s and "Подтвердите" in fixed:
                    return True
            except Exception:
                return True
        return False

    def _fix_mojibake(self, value: str) -> str:
        """Починить текст вида 'Ð\x9f...' (UTF-8, интерпретированный как latin-1)."""
        if not isinstance(value, str):
            return value
        if "Ð" not in value and "Ñ" not in value:
            return value
        try:
            fixed = value.encode("latin-1").decode("utf-8")
            return fixed
        except Exception:
            return value
