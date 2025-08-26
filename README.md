# 🎬 IPTV EPG Collector

[![CI](https://github.com/yhtyyar/cinema-epg-collector/actions/workflows/ci.yml/badge.svg)](https://github.com/yhtyyar/cinema-epg-collector/actions/workflows/ci.yml)

Полнофункциональное приложение для сбора, обработки и отображения данных IPTV EPG с фокусом на фильмы. Включает backend API на FastAPI и современный frontend на React + TypeScript.

## 🚀 Быстрый запуск через Docker

**Для новичков**: Следуйте этой инструкции пошагово, и у вас всё получится!

### Предварительные требования

1. **Docker Desktop** - [Скачать и установить](https://www.docker.com/products/docker-desktop/)
2. **Git** - [Скачать и установить](https://git-scm.com/downloads)

### Шаг 1: Клонирование проекта

```bash
# Клонируем репозиторий
git clone https://github.com/yhtyyar/cinema-epg-collector.git
cd cinema-epg-collector
```

### Шаг 2: Автоматический запуск (рекомендуется)

**Windows:**
```cmd
# Запуск одним кликом
scripts\start.bat
```

**Linux/macOS:**
```bash
# Запуск одной командой
./scripts/start.sh
```

### Шаг 2 (альтернативный): Ручной запуск

```bash
# Запускаем всё приложение одной командой
docker-compose up -d

# Проверяем статус контейнеров
docker-compose ps
```

**Готово!** Приложение доступно по адресам:
- 🌐 **Frontend**: http://localhost:3000
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API документация**: http://localhost:8000/docs

### Шаг 3: Первичная настройка данных

```bash
# Загружаем и обрабатываем EPG данные
docker-compose exec backend python -m epg_collector.cli run-all
```

## 🛠️ Режим разработки

### Запуск для разработки

```bash
# Запуск в режиме разработки с hot-reload
docker-compose -f docker-compose.dev.yml up -d

# Просмотр логов
docker-compose -f docker-compose.dev.yml logs -f
```

**Адреса в режиме разработки:**
- 🌐 **Frontend (Vite)**: http://localhost:5173
- 🔧 **Backend API**: http://localhost:8000
- 📚 **API документация**: http://localhost:8000/docs

### Полезные команды для разработки

```bash
# Остановка всех контейнеров
docker-compose down

# Пересборка контейнеров
docker-compose build --no-cache

# Просмотр логов конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend

# Выполнение команд внутри контейнера
docker-compose exec backend bash
docker-compose exec backend python -m epg_collector.cli --help

# Очистка всех Docker данных (осторожно!)
docker system prune -a
```

## 🔧 Конфигурация

### Настройка API ключей

1. **Создайте файл `.env`** (скопируйте из `.env.example`):
```bash
cp .env.example .env
```

2. **Отредактируйте `.env`** и укажите свои API ключи:
```env
# КиноПоиск API (получить на https://kinopoisk.dev)
KINOPOISK_API_KEY=ваш_ключ_здесь

# TMDB API (получить на https://www.themoviedb.org/settings/api)
TMDB_API_KEY=ваш_ключ_здесь

# IPTV настройки (замените на свои)
IPTV_HEADER_X_TOKEN=ваш_токен_здесь
```

### Структура проекта

```
.
├── backend/
│   ├── epg_collector/          # Основной Python пакет
│   │   ├── api/               # FastAPI приложение
│   │   ├── services/          # Бизнес-логика
│   │   ├── cli.py            # CLI команды
│   │   └── config.py         # Конфигурация
│   ├── data/                 # Данные и результаты
│   ├── logs/                 # Логи приложения
│   └── cache/                # HTTP кэш
├── frontend/
│   ├── src/
│   │   ├── components/       # React компоненты
│   │   ├── services/         # API клиенты
│   │   ├── types/           # TypeScript типы
│   │   └── pages/           # Страницы приложения
│   └── dist/                # Собранное приложение
├── docker-compose.yml        # Продакшен конфигурация
├── docker-compose.dev.yml    # Разработка конфигурация
└── README.md                # Эта документация
```

## 📋 CLI команды

```bash
# Все команды выполняются внутри backend контейнера
docker-compose exec backend python -m epg_collector.cli КОМАНДА

# Основные команды:
run-all                    # Полный цикл: загрузка → фильтрация → обогащение
fetch-epg-cmd             # Загрузка EPG данных
filter-movies-cmd         # Фильтрация фильмов
enrich                    # Обогащение данными КиноПоиска/TMDB

# Работа с каналами:
fetch-playlist-cmd        # Загрузка списка каналов
fetch-epg-for-playlist    # Загрузка EPG по каналам
filter-epg-movies         # Фильтрация фильмов по каналам
download-posters-epg-movies # Скачивание постеров
```

## 🚨 Решение проблем

### Проблема: Контейнеры не запускаются

```bash
# Проверьте статус Docker
docker --version
docker-compose --version

# Проверьте логи
docker-compose logs

# Пересоберите образы
docker-compose build --no-cache
```

### Проблема: Frontend не загружается

```bash
# Проверьте, что backend запущен
curl http://localhost:8000/healthz

# Проверьте логи frontend
docker-compose logs frontend

# Перезапустите frontend
docker-compose restart frontend
```

### Проблема: API возвращает ошибки

```bash
# Проверьте конфигурацию
docker-compose exec backend env | grep -E "(IPTV|KINOPOISK|TMDB)"

# Проверьте логи backend
docker-compose logs backend

# Проверьте health check
curl http://localhost:8000/healthz
```

### Проблема: Нет данных о фильмах

```bash
# Запустите загрузку данных
docker-compose exec backend python -m epg_collector.cli run-all

# Проверьте наличие файлов данных
docker-compose exec backend ls -la data/

# Проверьте логи обработки
docker-compose exec backend tail -f logs/app.log
```

## 🔍 Мониторинг

### Health Checks

```bash
# Проверка состояния всех сервисов
curl http://localhost:8000/healthz  # Backend
curl http://localhost:3000/health   # Frontend

# Проверка через Docker
docker-compose ps
```

### Логи

```bash
# Просмотр всех логов
docker-compose logs -f

# Логи конкретного сервиса
docker-compose logs -f backend
docker-compose logs -f frontend

# Логи приложения (внутри контейнера)
docker-compose exec backend tail -f logs/app.log
```

## 🎯 Возможности
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
