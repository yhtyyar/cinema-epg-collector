# Руководство по настройке на Ubuntu для IPTV EPG Collector

Это руководство содержит пошаговые инструкции для ручного развертывания IPTV EPG Collector на сервере Ubuntu.

## 📋 Предварительные требования

- Ubuntu 20.04 или новее
- Доступ root или sudo
- Минимум 2 ГБ ОЗУ
- Минимум 10 ГБ свободного места на диске

## 🛠️ Шаги установки

### 1. Обновление системных пакетов
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Установка необходимых пакетов
```bash
sudo apt install -y python3 python3-pip python3-venv curl git nodejs npm
```

### 3. Клонирование репозитория
```bash
git clone https://github.com/yhtyyar/cinema-epg-collector.git
cd cinema-epg-collector
```

### 4. Настройка виртуального окружения Python
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Настройка переменных окружения
```bash
cp .env.example .env
# Отредактируйте файл .env с вашими настройками
nano .env
```

Важные переменные для настройки:
- `TMDB_API_KEY` - Получите это на https://www.themoviedb.org/settings/api
- `IPTV_HEADER_X_TOKEN` - Ваш токен провайдера IPTV

### 6. Создание необходимых директорий
```bash
mkdir -p data/posters cache logs
```

### 7. Запуск конвейера сбора данных
```bash
python -m epg_collector.cli run-all
```

### 8. Запуск сервера API
```bash
uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000
```

API будет доступен по адресу `http://your-server-ip:8000`

### 9. Настройка фронтенда (опционально)
```bash
cd frontend
npm ci
npm run build
```

Разместите собранные файлы фронтенда любым веб-сервером (nginx, Apache и т.д.)

## 🔧 Запуск как сервис (опционально)

Для запуска приложения как сервис systemd:

### 1. Создайте файл сервиса systemd:
```bash
sudo nano /etc/systemd/system/cinema-epg.service
```

### 2. Добавьте следующее содержимое:
```ini
[Unit]
Description=Cinema EPG Collector
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/cinema-epg-collector
ExecStart=/path/to/cinema-epg-collector/venv/bin/uvicorn epg_collector.api.app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 3. Включите и запустите сервис:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cinema-epg
sudo systemctl start cinema-epg
```

## 🔄 Обновление данных

Для обновления данных фильмов запустите:
```bash
cd /path/to/cinema-epg-collector
source venv/bin/activate
python -m epg_collector.cli run-all
```

Вы можете настроить задание cron для автоматического ежедневного обновления данных:
```bash
# Добавьте в crontab (crontab -e)
0 2 * * * cd /path/to/cinema-epg-collector && /path/to/cinema-epg-collector/venv/bin/python -m epg_collector.cli run-all
```

## 📁 Структура директорий

После настройки ваша директория будет содержать:
- `data/` - Содержит собранные данные и постеры
- `cache/` - Кэш HTTP-запросов
- `logs/` - Логи приложения
- `venv/` - Виртуальное окружение Python (создается во время настройки)

## 🔒 Вопросы безопасности

1. Измените порт API по умолчанию (8000), если вы expose его в интернет
2. Настройте обратный прокси (nginx) с SSL/TLS
3. Ограничьте доступ к API с помощью правил брандмауэра
4. Используйте надежную аутентификацию для производственных развертываний

## 🆘 Устранение неполадок

### Распространенные проблемы:

1. **Ошибки доступа**: Убедитесь, что пользователь, запускающий сервис, имеет права на чтение/запись в директории data, cache и logs.

2. **Порт уже используется**: Измените порт в команде uvicorn или остановите процесс, использующий порт:
   ```bash
   sudo lsof -i :8000
   kill -9 <PID>
   ```

3. **Отсутствующие зависимости**: Убедитесь, что все необходимые пакеты установлены:
   ```bash
   pip install -r requirements.txt
   ```

4. **Проблемы с API TMDB**: Проверьте правильность и активность вашего ключа API TMDB.

### Проверка логов:

Логи приложения записываются в директорию `logs/` и в stdout при запуске сервера.

Для логов сервиса systemd:
```bash
sudo journalctl -u cinema-epg -f
```