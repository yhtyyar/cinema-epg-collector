# IPTV EPG Collector - Руководство по ручному развертыванию

Этот проект собирает данные EPG IPTV, фильтрует фильмы, обогащает их данными TMDB и предоставляет REST API для доступа к данным.

## 📋 Предварительные требования

- Ubuntu 20.04 или новее
- Python 3.8+
- Node.js 16+ (для фронтенда)
- Ключ API TMDB (бесплатно на https://www.themoviedb.org/settings/api)

## 🛠️ Ручная установка

### 1. Клонирование репозитория
```bash
git clone https://github.com/yhtyyar/cinema-epg-collector.git
cd cinema-epg-collector
```

### 2. Настройка виртуального окружения Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Настройка переменных окружения
```bash
cp .env.example .env
# Отредактируйте файл .env с вашим ключом TMDB API и другими настройками
nano .env
```

### 4. Создание необходимых директорий
```bash
mkdir -p data/posters cache logs
```

### 5. Запуск конвейера сбора данных
```bash
python -m epg_collector.cli run-all
```

### 6. Запуск сервера API
```bash
uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000
```

### 7. Сборка и запуск фронтенда (опционально)
```bash
cd frontend
npm ci
npm run build
# Разместите собранные файлы любым веб-сервером
```

## 📊 Конечные точки API

- `GET /api/movies` - Список фильмов с пагинацией и фильтрами
- `GET /api/movies/{id}` - Получить фильм по ID
- `GET /api/movies/search?q=...` - Поиск фильмов по названию
- `GET /healthz` - Проверка состояния
- `GET /static/posters/...` - Доступ к загруженным постерам
- `POST /api/collect-data` - Запустить сбор данных в фоновом режиме (новое)

## 🎬 Команды ручного конвейера

Вы можете запускать отдельные шаги конвейера:

```bash
# 1. Получить данные EPG
python -m epg_collector.cli fetch-epg-cmd

# 2. Отфильтровать фильмы
python -m epg_collector.cli filter-movies-cmd

# 3. Обогатить данными TMDB
python -m epg_collector.cli enrich
```

## ⚙️ Переменные окружения

Основные переменные в файле `.env`:
- `TMDB_API_KEY` - Обязатен для обогащения данных фильмов
- `IPTV_HEADER_X_TOKEN` - Ваш токен провайдера IPTV
- `LOG_LEVEL` - Уровень детализации логов (INFO, DEBUG и т.д.)
- `AUTO_RUN_PIPELINE` - Установите в `true`, чтобы автоматически запускать сбор данных при старте API (по умолчанию `false`)

## 📁 Структура директорий

- `data/` - Содержит собранные данные и постеры
- `cache/` - Кэш HTTP-запросов
- `logs/` - Логи приложения
- `epg_collector/` - Основное приложение Python
- `frontend/` - Приложение фронтенда React

## 🔄 Обновление данных

Для обновления данных фильмов можно использовать один из следующих способов:

1. **Через CLI:**
```bash
python -m epg_collector.cli run-all
```

2. **Через API (в фоновом режиме):**
```bash
curl -X POST http://localhost:8000/api/collect-data
```

API будет автоматически обслуживать обновленные данные.

## 📖 Дополнительная документация

- [UBUNTU_SETUP.md](UBUNTU_SETUP.md) - Подробное руководство по установке на Ubuntu
- [REFACTORED.md](REFACTORED.md) - Документация по рефакторингу проекта
- [frontend/README.md](frontend/README.md) - Документация по фронтенду

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

### 🔄 Фронтенд улучшения

Фронтенд был переработан с учетом современных практик разработки:
- Улучшена типобезопасность с помощью TypeScript
- Добавлены пользовательские хуки для повторного использования логики
- Оптимизирована производительность с помощью мемоизации
- Улучшена обработка ошибок с помощью Error Boundary
- Добавлены константы и утилиты для лучшей организации кода
- Улучшена структура компонентов
- Добавлена поддержка debounce для поиска
- Улучшена доступность и пользовательский опыт

Более подробную информацию о фронтенде можно найти в [frontend/README.md](frontend/README.md).