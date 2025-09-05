# IPTV EPG Collector - Manual Deployment Guide

This project collects IPTV EPG data, filters movies, enriches them with TMDB data, and provides a REST API for accessing the data.

## 📋 Prerequisites

- Ubuntu 20.04 or later
- Python 3.8+
- Node.js 16+ (for frontend)
- TMDB API key (free at https://www.themoviedb.org/settings/api)

## 🛠️ Manual Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd cinema-epg-collector
```

### 2. Set Up Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables
```bash
cp .env.example .env
# Edit .env file with your TMDB API key and other settings
nano .env
```

### 4. Create Required Directories
```bash
mkdir -p data/posters cache logs
```

### 5. Run Data Collection Pipeline
```bash
python -m epg_collector.cli run-all
```

### 6. Start the API Server
```bash
uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000
```

### 7. Build and Run Frontend (Optional)
```bash
cd frontend
npm ci
npm run build
# Serve the built files with any web server
```

## 📊 API Endpoints

- `GET /api/movies` - List movies with pagination and filters
- `GET /api/movies/{id}` - Get movie by ID
- `GET /api/movies/search?q=...` - Search movies by title
- `GET /healthz` - Health check endpoint
- `GET /static/posters/...` - Access downloaded posters

## 🎬 Manual Pipeline Commands

You can run individual steps of the pipeline:

```bash
# 1. Fetch EPG data
python -m epg_collector.cli fetch-epg-cmd

# 2. Filter movies
python -m epg_collector.cli filter-movies-cmd

# 3. Enrich with TMDB data
python -m epg_collector.cli enrich
```

## ⚙️ Environment Variables

Key variables in `.env`:
- `TMDB_API_KEY` - Required for movie data enrichment
- `IPTV_HEADER_X_TOKEN` - Your IPTV provider token
- `LOG_LEVEL` - Logging verbosity (INFO, DEBUG, etc.)

## 📁 Directory Structure

- `data/` - Contains collected data and posters
- `cache/` - HTTP request cache
- `logs/` - Application logs
- `epg_collector/` - Main Python application
- `frontend/` - React frontend application

## 🔄 Data Update

To update the movie data, run:
```bash
python -m epg_collector.cli run-all
```

The API will automatically serve the updated data.

## 🚀 Возможности
- **Автоматизированный Docker deployment** с одной командой
- Запрос к IPTV EPG API с кастомными заголовками
- Фильтрация по категории, содержащей "Х/ф"
- **Обогащение данных фильмами через TMDB API** (The Movie Database)
- Кэширование HTTP-запросов и результатов TMDB
- Надёжный HTTP-клиент с retry и таймаутами
- Конфигурация через `.env`
- Структурированное логирование в файл и консоль
- Удобный CLI через Typer
- Скачивание постеров фильмов в `data/posters/` и добавление локальной ссылки `poster_local` в `enriched_movies.json`
  - **Источник постеров: TMDB (приоритет), затем EPG preview**
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
│  ├─ tmdb.py
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

## 🚀 Быстрый старт (Docker - Рекомендуется)

### Автоматический запуск одной командой:
```bash
./deploy.sh
```

### Ручная настройка:
1. **Получите TMDB API ключ** на https://www.themoviedb.org/settings/api
2. **Настройте окружение:**
```bash
cp .env.example .env
# Отредактируйте .env и добавьте ваш TMDB_API_KEY
```
3. **Запустите проект:**
```bash
./deploy.sh deploy dev  # Режим разработки
./deploy.sh deploy prod # Продакшн режим
```

### Альтернативный запуск (без скрипта):
```bash
docker-compose up --build -d
```

## 🛠️ Локальная разработка (без Docker)
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env
# Настройте .env файл
python -m epg_collector.cli run-all
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

## 📊 Результаты обогащения
Файл `data/enriched_movies.json` содержит исходные поля EPG, блок `tmdb_data` и локальную ссылку на постер:

```json
{
  "title": "Пример фильма",
  "preview": "http://.../pic/12345?size=320x240",
  "tmdb_data": {
    "source": "tmdb",
    "name": "Пример фильма",
    "year": 2020,
    "rating_imdb": 7.5,
    "genres": ["Action", "Drama"],
    "poster_url": "https://image.tmdb.org/t/p/w500/poster.jpg"
  },
  "poster_local": "data/posters/19100159534-primer-filma.jpg",
  "poster_source": "tmdb|preview"
}
```

## ⚙️ Переменные окружения (.env)
- **TMDB_API_KEY** - **ОБЯЗАТЕЛЬНО**: API ключ от TMDB для обогащения данных
- IPTV_BASE_URL (по умолчанию: https://pl.iptv2021.com/api/v4/epg)
- IPTV_PARAMS_* (см. .env.example)
- IPTV_HEADER_HOST, IPTV_HEADER_UA, IPTV_HEADER_X_LHD_AGENT, IPTV_HEADER_X_TOKEN
- HTTP_TIMEOUT, HTTP_RETRIES, HTTP_BACKOFF
- CACHE_ENABLED, CACHE_PATH, CACHE_EXPIRE
- TMDB_BASE_URL, TMDB_IMAGE_BASE (необязательно)
- LOG_LEVEL (INFO|DEBUG|WARNING|ERROR)
- AUTO_RUN_PIPELINE (true|false) - автозапуск пайплайна при старте

## 🎬 Заметки по TMDB
- Получите бесплатный API ключ на https://www.themoviedb.org/settings/api
- TMDB предоставляет качественные метаданные фильмов и постеры
- Поддерживается поиск на русском языке

## REST API
API реализован на FastAPI и отдаёт унифицированные данные из `data/enriched_movies.json`.

### 🚀 Запуск API

**Рекомендуемый способ (Docker):**
```bash
./deploy.sh deploy
```

**Альтернативные способы:**
```bash
# Docker Compose
docker-compose up --build -d

# Локально
uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000
```

### Эндпоинты
- `GET /api/movies` — список фильмов с пагинацией и фильтрами
  - Параметры: `page` (int), `per_page` (int, 1..200), `genre` (str), `year` (int), `rating_gte` (float), `source` (str: kinopoisk|tmdb|preview|null), `q` (str)
- `GET /api/movies/{id}` — фильм по идентификатору
- `GET /api/movies/search?q=...` — поиск по названию (EPG/TMDB)
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
      "tmdb_data": {
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

## 📋 Управление проектом

### Доступные команды deploy.sh:
```bash
./deploy.sh deploy [dev|prod|frontend]  # Развертывание
./deploy.sh status                      # Статус сервисов
./deploy.sh pipeline                    # Запуск пайплайна вручную
./deploy.sh logs [service]              # Просмотр логов
./deploy.sh stop                        # Остановка сервисов
./deploy.sh restart                     # Перезапуск сервисов
./deploy.sh cleanup                     # Очистка Docker ресурсов
./deploy.sh help                        # Справка
```

### Доступные эндпоинты:
- 🌐 **API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs
- 🏥 **Health Check**: http://localhost:8000/healthz
- 📊 **Movies API**: http://localhost:8000/api/movies

## 📝 Changelog

### v1.0.0 - Docker Edition
- **Полное удаление Kinopoisk** - используется только TMDB API
- **Docker-based deployment** с автоматизированным скриптом
- **Nginx reverse proxy** для продакшн развертывания
- **Health checks** и мониторинг сервисов
- **Автоматический пайплайн** при запуске контейнера
- **Security improvements** - non-root пользователь в контейнере
- **Comprehensive logging** и error handling

### v0.2.0
- Исправлен парсинг EPG: устойчивый JSON-декодинг (`utf-8` → `cp1251` → `latin-1`), защита от не-JSON ответов (капча) с логированием сэмпла
- Постеры: жёстко локальная раздача через `/static`; понижен минимальный валидный размер до 4KB; проверка магических байт сохранена
- TMDB как приоритетный источник постеров при наличии `TMDB_API_KEY`
- Frontend: добавлен dev proxy `/static`, `onError`-фолбэк для битых изображений, декларации типов
- CI: добавлена задача сборки фронтенда (typecheck + build) на Node 20
