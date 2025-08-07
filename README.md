# CinemaEPGCollector

Микросервис для автоматического сбора телепрограммы (EPG) и информации о фильмах с каналов IPTV.

## Функциональность

- 🔄 Автоматический сбор плейлиста каналов
- 📺 Регулярный сбор EPG (Electronic Program Guide) для всех каналов
- 🎬 Фильтрация и обработка данных о фильмах и программах
- 🌐 REST API для доступа к данным
- 🔐 Система аутентификации и авторизации
- ⏰ Поддержка временных зон
- 📊 Мониторинг и статистика

## Технологический стек

- **Язык**: Go 1.21+
- **Web Framework**: Gin
- **База данных**: PostgreSQL
- **Кэширование**: Redis
- **ORM**: GORM
- **Планировщик**: Cron
- **Контейнеризация**: Docker & Docker Compose
- **Логирование**: Logrus

## Структура проекта

```
cinema-epg-collector/
├── cmd/server/          # Точка входа приложения
├── internal/
│   ├── api/            # HTTP API handlers, middleware, routes
│   ├── collector/      # Сборщики данных (playlist, epg)
│   ├── storage/        # Слой работы с БД (postgres, redis)
│   ├── config/         # Конфигурация приложения
│   └── models/         # Модели данных
├── pkg/                # Переиспользуемые пакеты
│   ├── httpclient/     # HTTP клиент
│   └── logger/         # Логирование
├── migrations/         # Миграции БД
├── docker/            # Docker файлы
└── docs/              # Документация
```

## Быстрый старт

### Предварительные требования

- Go 1.21+
- Docker и Docker Compose
- PostgreSQL 15+
- Redis 7+

### Установка Go (Windows)

1. Скачайте Go с официального сайта: https://golang.org/dl/
2. Выберите версию для Windows (go1.21.x.windows-amd64.msi)
3. Запустите установщик и следуйте инструкциям
4. Перезапустите командную строку
5. Проверьте установку: `go version`

### Запуск с Docker

1. Клонируйте проект:
```bash
git clone <repository-url>
cd cinema-epg-collector
```

2. Запустите сервисы:
```bash
docker-compose up -d
```

3. Проверьте статус:
```bash
curl http://localhost:8080/health
```

### Локальная разработка

1. Установите зависимости:
```bash
go mod tidy
```

2. Запустите PostgreSQL и Redis:
```bash
docker-compose up -d postgres redis
```

3. Запустите приложение:
```bash
go run cmd/server/main.go
```

## API Endpoints

### Системные

- `GET /health` - Проверка здоровья сервиса
- `GET /stats` - Статистика (количество каналов и программ)

### Сбор данных

- `POST /collect/playlist` - Запуск сбора плейлиста
- `POST /collect/epg?tz=3` - Запуск сбора EPG

### Данные

- `GET /channels` - Список всех каналов
- `GET /channels/{id}/epg` - EPG для конкретного канала

## Конфигурация

Настройки находятся в файле `config.yaml`:

```yaml
server:
  port: "8080"
  host: "localhost"

database:
  host: "localhost"
  port: 5432
  user: "postgres"
  password: "password"
  dbname: "cinema_epg"

api:
  playlist_url: "https://pl.iptv2021.com/api/v4/playlist"
  epg_url: "https://pl.iptv2021.com/api/v4/epg"
```

## Автоматический сбор данных

Сервис автоматически собирает данные по расписанию:

- **Плейлист**: ежедневно в 6:00
- **EPG**: каждые 2 часа

## Модели данных

### Channel (Канал)
- ID, ExternalID, Name, IconURL
- StreamURLs (список ссылок на трансляцию)
- Category, CreatedAt, UpdatedAt

### EPGProgram (Программа)
- Title, Description, StartTime, EndTime
- Category, Genre, AgeRating, Year, Rating
- PosterURL, Duration

### StreamURL (Ссылка на поток)
- URL, Quality, Type (hls, dash)

## Разработка

### Добавление новых коллекторов

1. Создайте пакет в `internal/collector/`
2. Реализуйте интерфейс сбора данных
3. Добавьте в планировщик в `main.go`

### Тестирование

```bash
# Запуск тестов
go test ./...

# Тестирование с покрытием
go test -cover ./...
```

## Мониторинг

Сервис предоставляет метрики для мониторинга:

- Количество каналов в БД
- Количество программ в БД
- Статус последнего сбора данных

## Безопасность

- Все внешние запросы логируются
- Поддержка HTTPS
- Валидация входных данных
- Rate limiting (планируется)

## Лицензия

MIT License

## Контакты

Для вопросов и предложений создавайте Issues в репозитории.
