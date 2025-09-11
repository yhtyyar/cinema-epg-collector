# Cinema EPG Collector

Сборщик EPG данных для IPTV с фильтрацией фильмов, обогащением через TMDB API и локальной доставкой постеров.

## 🎯 Возможности

- Скачивание EPG из IPTV API
- Фильтрация фильмов по категории "Х/ф"
- Обогащение данных через TMDB API
- Локальная доставка постеров (избегая блокировки CDN)
- REST API для доступа к данным
- Современный веб-интерфейс
- Docker-контейнеризация
- Структурированное логирование
- Повторные попытки HTTP-запросов с экспоненциальной задержкой
- HTTP-кэширование и кэширование результатов TMDB

## 🏗️ Архитектура

```
┌─────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   IPTV API      │───▶│  Backend (FastAPI) │───▶│  Frontend (React)│
└─────────────────┘    └──────────────────┘    └──────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌─────────────┐         ┌─────────────────┐
                       │  TMDB API   │         │   Web Browser   │
                       └─────────────┘         └─────────────────┘
```

## 🚀 Быстрый старт

### Docker (рекомендуется)

```bash
# Клонировать репозиторий
git clone https://github.com/yhtyyar/cinema-epg-collector.git
cd cinema-epg-collector

# Скопировать и настроить .env
cp .env.example .env
# Отредактировать .env, добавив TMDB_API_KEY

# Запустить все сервисы
docker-compose up --build -d

# API будет доступен по адресу: http://localhost:8000
# Веб-интерфейс будет доступен по адресу: http://localhost:3000
```

### Локальный запуск

```bash
# Клонировать репозиторий
git clone https://github.com/yhtyyar/cinema-epg-collector.git
cd cinema-epg-collector

# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установить зависимости
pip install -r requirements.txt

# Скопировать и настроить .env
cp .env.example .env
# Отредактировать .env, добавив TMDB_API_KEY

# Запустить API сервер
python start_api.py --host 0.0.0.0 --port 8000
# или использовать uvicorn напрямую:
# uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000

# В другой консоли запустить фронтенд
cd frontend
npm install
npm run dev
```

## 📁 Структура проекта

```
.
├── epg_collector/          # Бэкенд приложение
│   ├── api/                # FastAPI REST API
│   ├── cli.py              # CLI интерфейс
│   ├── config.py           # Конфигурация
│   ├── http_client.py      # HTTP клиент с повторными попытками
│   ├── iptv_api.py         # Загрузчик EPG
│   ├── filters.py          # Фильтры данных
│   ├── tmdb.py             # Интеграция с TMDB
│   ├── posters.py          # Загрузчик постеров
│   └── logging_config.py   # Настройка логирования
├── frontend/               # Фронтенд приложение (React/Vite)
├── data/                   # Данные (EPG, фильмы, постеры)
├── cache/                  # Кэш HTTP и TMDB
├── logs/                   # Логи приложения
├── docker-compose.yml      # Docker Compose конфигурация
├── Dockerfile              # Dockerfile для бэкенда
└── requirements.txt        # Зависимости Python
```

## ⚙️ Конфигурация

Все настройки задаются через файл [.env](file:///C:/Users/User/CascadeProjects/cinema-epg-collector/.env) или переменные окружения:

```env
# IPTV API
IPTV_BASE_URL=https://pl.iptv2021.com/api/v4/epg
IPTV_PARAMS_ID=17305
IPTV_HEADER_X_TOKEN=your_token_here

# TMDB API (обязательно)
TMDB_API_KEY=your_tmdb_api_key_here

# API настройки
API_HOST=0.0.0.0
API_PORT=8000

# Pipeline настройки
AUTO_RUN_PIPELINE=false
SKIP_ENRICHMENT_IF_EXISTS=true
```

### Основные параметры

- `TMDB_API_KEY` - API ключ для доступа к TMDB (обязательно)
- `API_HOST` - Хост для API сервера (по умолчанию 0.0.0.0)
- `API_PORT` - Порт для API сервера (по умолчанию 8000)
- `AUTO_RUN_PIPELINE` - Автоматический запуск пайплайна при старте API
- `SKIP_ENRICHMENT_IF_EXISTS` - Пропустить обогащение если данные уже существуют

## 🛠️ Использование

### CLI команды

```bash
# Активировать виртуальное окружение
source venv/bin/activate

# Загрузить EPG данные
python -m epg_collector.cli fetch-epg

# Отфильтровать фильмы
python -m epg_collector.cli filter-movies

# Обогатить данные через TMDB
python -m epg_collector.cli enrich

# Выполнить полный цикл
python -m epg_collector.cli run-all
```

### API эндпоинты

- `GET /healthz` - Проверка состояния
- `GET /api/movies` - Список фильмов с фильтрацией и пагинацией
- `GET /api/movies/{id}` - Получить фильм по ID
- `GET /api/movies/search` - Поиск фильмов
- `POST /api/collect-data` - Запустить сбор данных в фоне
- `GET /api/data-status` - Получить статус данных
- `GET /static/posters/{filename}` - Доставка постеров

### Запуск API с настраиваемым хостом и портом

```bash
# Запустить API с кастомными параметрами
python start_api.py --host 194.35.48.118 --port 8080
```

## 🌐 Веб-интерфейс

Фронтенд доступен по адресу [http://localhost:3000](http://localhost:3000) после запуска.

## 🐳 Docker

### Сборка и запуск

```bash
# Собрать и запустить все сервисы
docker-compose up --build -d

# Остановить сервисы
docker-compose down
```

### Конфигурация Docker

Все настройки передаются через переменные окружения в `docker-compose.yml`.

## 📊 Мониторинг

### Логи

Логи доступны в директории `logs/` или через `docker-compose logs`.

### Health Checks

- API: `GET /healthz`
- Данные: `GET /api/data-status`

## 🔧 Устранение неполадок

### Проблемы с TMDB

Убедитесь, что `TMDB_API_KEY` установлен правильно в [.env](file:///C:/Users/User/CascadeProjects/cinema-epg-collector/.env).

### Проблемы с IPTV API

Проверьте правильность `IPTV_HEADER_X_TOKEN` в [.env](file:///C:/Users/User/CascadeProjects/cinema-epg-collector/.env).

### Проблемы с постерами

Проверьте, что директория `data/posters` существует и доступна для записи.

## 📈 Производительность

- HTTP-кэширование для уменьшения нагрузки на внешние API
- Повторные попытки с экспоненциальной задержкой для надежности
- Асинхронная обработка фоновых задач
- Эффективное использование памяти

## 📚 Документация API

После запуска API документация доступна по адресу [http://localhost:8000/docs](http://localhost:8000/docs).

## 🤝 Вклад в проект

1. Форкните репозиторий
2. Создайте ветку для вашей функции (`git checkout -b feature/AmazingFeature`)
3. Зафиксируйте изменения (`git commit -m 'Add some AmazingFeature'`)
4. Запушьте ветку (`git push origin feature/AmazingFeature`)
5. Откройте Pull Request

## 📄 Лицензия

Этот проект лицензирован по лицензии MIT - см. файл [LICENSE](file:///C:/Users/User/CascadeProjects/cinema-epg-collector/LICENSE) для подробностей.

## 🙏 Благодарности

- [TMDB](https://www.themoviedb.org/) за API
- [FastAPI](https://fastapi.tiangolo.com/) за фреймворк
- [React](https://reactjs.org/) за фронтенд библиотеку
```

parameter>