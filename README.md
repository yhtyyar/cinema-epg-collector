# IPTV EPG Collector

[![CI](https://github.com/yhtyyar/cinema-epg-collector/actions/workflows/ci.yml/badge.svg)](https://github.com/yhtyyar/cinema-epg-collector/actions/workflows/ci.yml)

Модульный профессиональный проект для работы с IPTV EPG данными: загрузка, фильтрация по фильмам (категория "Х/ф"), обогащение и локальная раздача постеров, backend API на FastAPI и современный фронтенд на Vite + React.

## Возможности
- Запрос к IPTV EPG API с кастомными заголовками
- Фильтрация по категории, содержащей "Х/ф"
- Обогащение данных фильмами с КиноПоиска (API или веб-поиск как fallback)
- Кэширование HTTP-запросов и результатов КиноПоиска
- Надёжный HTTP-клиент с retry и таймаутами
- Конфигурация через `.env`
- Логирование в файл и консоль
- Удобный CLI через Typer
- Скачивание постеров фильмов в `data/posters/` и добавление локальной ссылки `poster_local` в `enriched_movies.json`
  - Источник постеров: приоритет TMDB (если доступен `TMDB_API_KEY`), затем Kinopoisk, затем EPG preview
  - Поле `poster_source` фиксирует использованный источник
  - Валидация изображений (Content-Type, магические байты JPG/PNG/WEBP, минимальный размер)
  - Постеры отдаются фронтенду ТОЛЬКО локально через `/static/posters/...` для надёжной работы без блокировок CDN

## Структура проекта
```
.
├─ epg_collector/
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ config.py
│  ├─ http_client.py
│  ├─ iptv_api.py
│  ├─ filters.py
│  ├─ kinopoisk.py
│  ├─ logging_config.py
│  └─ posters.py
├─ data/              # результаты и артефакты (raw_epg.json, movies.json, enriched_movies.json, posters/)
│  └─ posters/
├─ frontend/          # Vite + React SPA клиент (dev proxy к бэкенду)
├─ cache/             # http_cache.sqlite и кэш КиноПоиска
├─ logs/              # app.log
├─ .env.example
├─ requirements.txt
└─ README.md
```

## Быстрый старт
1. Установите зависимости:
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
2. Создайте `.env` на основе `.env.example` и заполните значения.
3. Запуск CLI:
```bash
python -m epg_collector.cli run-all
```
Либо по шагам:
```bash
python -m epg_collector.cli fetch-epg-cmd
python -m epg_collector.cli filter-movies-cmd
python -m epg_collector.cli enrich
```

## Frontend (Vite + React)

Локальный запуск фронтенда с проксированием запросов к бэкенду и статике постеров:

```bash
cd frontend
npm ci
npm run dev
# Откройте http://localhost:5173
```

Dev-прокси настроен в `frontend/vite.config.ts` на `http://localhost:8000` для путей `/api` и `/static`.
Продакшн-сборка:

```bash
cd frontend
npm run build
```

## Результаты обогащения
Файл `data/enriched_movies.json` содержит исходные поля EPG, блок `kinopoisk` и локальную ссылку на постер:

```json
{
  "title": "Пример фильма",
  "preview": "http://.../pic/12345?size=320x240",
  "kinopoisk": {
    "source": "api|web",
    "kp_id": 123456,
    "name": "Пример фильма",
    "year": 2020,
    "poster_url": "https://.../poster.jpg"
  },
  "poster_local": "data/posters/19100159534-primer-filma.jpg",
  "poster_source": "kinopoisk|tmdb|preview"
}
```

## Переменные окружения (.env)
- IPTV_BASE_URL (по умолчанию: https://pl.iptv2021.com/api/v4/epg)
- IPTV_PARAMS_* (см. .env.example)
- IPTV_HEADER_HOST, IPTV_HEADER_UA, IPTV_HEADER_X_LHD_AGENT, IPTV_HEADER_X_TOKEN
- HTTP_TIMEOUT, HTTP_RETRIES, HTTP_BACKOFF
- CACHE_ENABLED, CACHE_PATH, CACHE_EXPIRE
- KINOPOISK_API_KEY (опционально; если указан, используется api.kinopoisk.dev)
- TMDB_API_KEY (опционально; при наличии включается поиск постеров в TMDB)
- TMDB_BASE_URL, TMDB_IMAGE_BASE (необязательно)
- LOG_LEVEL (INFO|DEBUG|WARNING|ERROR)

## Заметки по КиноПоиску
- Рекомендуется использовать `api.kinopoisk.dev` (нужен API-ключ). Без ключа используется веб-поиск (может быть ограничен антибот-защитой).

## REST API
API реализован на FastAPI и отдаёт унифицированные данные из `data/enriched_movies.json`.

### Запуск API
```bash
# Локально
uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000

# Через Docker
docker build -t cinema-epg-api .
docker run --rm -p 8000:8000 --env-file .env -v %cd%/data:/app/data cinema-epg-api
# (Linux/macOS): заменить %cd% на $(pwd)
```

### Эндпоинты
- `GET /api/movies` — список фильмов с пагинацией и фильтрами
  - Параметры: `page` (int), `per_page` (int, 1..200), `genre` (str), `year` (int), `rating_gte` (float), `source` (str: kinopoisk|tmdb|preview|null), `q` (str)
- `GET /api/movies/{id}` — фильм по идентификатору
- `GET /api/movies/search?q=...` — поиск по названию (EPG/КП)
- `GET /healthz` — проверка состояния
- `GET /static/...` — статика из папки `data/` (например, локальные постеры `data/posters/...` доступны как `/static/posters/...`)

### Примеры
```bash
curl "http://localhost:8000/api/movies?page=1&per_page=50&genre=Боевик&rating_gte=6"
curl "http://localhost:8000/api/movies/19100159618"
curl "http://localhost:8000/api/movies/search?q=невидимка"
```

### OpenAPI/Swagger
- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### Формат ответа (пример)
```json
{
  "movies": [
    {
      "id": "19100159618",
      "epg_data": {
        "title": "Невидимка Сью",
        "description": "...",
        "broadcast_time": "2025-08-13T13:40:00",
        "preview_image": "http://..."
      },
      "kinopoisk_data": {
        "title": "...",
        "original_title": null,
        "year": 2019,
        "rating": 6.2,
        "description": null,
        "poster_url": "/static/posters/19100159618-item.jpg",
        "genres": ["Фэнтези", "Приключения"],
        "duration": null
      },
      "metadata": {
        "created_at": null,
        "updated_at": null,
        "source": "enriched"
      }
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 50,
    "total": 70,
    "pages": 2
  }
}
```

## Лицензия
MIT

## Changelog

### v0.2.0
- Исправлен парсинг EPG: устойчивый JSON-декодинг (`utf-8` → `cp1251` → `latin-1`), защита от не-JSON ответов (капча) с логированием сэмпла
- Постеры: жёстко локальная раздача через `/static`; понижен минимальный валидный размер до 4KB; проверка магических байт сохранена
- TMDB как приоритетный источник постеров при наличии `TMDB_API_KEY`; fallback: Kinopoisk → preview
- Frontend: добавлен dev proxy `/static`, `onError`-фолбэк для битых изображений, декларации типов
- CI: добавлена задача сборки фронтенда (typecheck + build) на Node 20
