#!/usr/bin/env python3
"""
Скрипт для запуска API с настраиваемым хостом и портом.
"""

import os
import sys
import argparse
from epg_collector.config import load_config

def main():
    parser = argparse.ArgumentParser(description="Запуск Cinema EPG Collector API")
    parser.add_argument("--host", help="Хост для API (по умолчанию из конфигурации)")
    parser.add_argument("--port", type=int, help="Порт для API (по умолчанию из конфигурации)")
    
    args = parser.parse_args()
    
    # Загружаем конфигурацию
    config = load_config()
    
    # Определяем хост и порт
    host = args.host if args.host is not None else config.api_host
    port = args.port if args.port is not None else config.api_port
    
    # Запускаем API сервер
    print(f"Запуск API сервера на {host}:{port}")
    
    # Импортируем и запускаем приложение
    from epg_collector.api.app import app
    import uvicorn
    
    uvicorn.run(
        "epg_collector.api.app:app",
        host=host,
        port=port,
        log_level=config.log_level.lower()
    )

if __name__ == "__main__":
    main()