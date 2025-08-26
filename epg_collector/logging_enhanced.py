"""Улучшенная система логирования с контекстом и метриками."""
from __future__ import annotations

import logging
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Dict, Optional, Callable
from pathlib import Path
import json


class ContextualLogger:
    """Логгер с контекстной информацией."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.context: Dict[str, Any] = {}
        
    def set_context(self, **kwargs):
        """Устанавливает контекст для логирования."""
        self.context.update(kwargs)
        
    def clear_context(self):
        """Очищает контекст."""
        self.context.clear()
        
    def _format_message(self, message: str) -> str:
        """Форматирует сообщение с контекстом."""
        if not self.context:
            return message
            
        context_str = " | ".join(f"{k}={v}" for k, v in self.context.items())
        return f"{message} | {context_str}"
        
    def debug(self, message: str, **kwargs):
        self.logger.debug(self._format_message(message), extra=kwargs)
        
    def info(self, message: str, **kwargs):
        self.logger.info(self._format_message(message), extra=kwargs)
        
    def warning(self, message: str, **kwargs):
        self.logger.warning(self._format_message(message), extra=kwargs)
        
    def error(self, message: str, **kwargs):
        self.logger.error(self._format_message(message), extra=kwargs)
        
    def exception(self, message: str, **kwargs):
        self.logger.exception(self._format_message(message), extra=kwargs)


class MetricsLogger:
    """Логгер для сбора метрик производительности."""
    
    def __init__(self, output_file: Optional[Path] = None):
        self.metrics: Dict[str, Any] = {}
        self.output_file = output_file or Path("logs/metrics.json")
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
    def record_metric(self, name: str, value: Any, tags: Optional[Dict[str, str]] = None):
        """Записывает метрику."""
        timestamp = time.time()
        metric_entry = {
            "timestamp": timestamp,
            "name": name,
            "value": value,
            "tags": tags or {}
        }
        
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append(metric_entry)
        
    def save_metrics(self):
        """Сохраняет метрики в файл."""
        try:
            with open(self.output_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logging.error(f"Не удалось сохранить метрики: {e}")
            
    @contextmanager
    def time_operation(self, operation_name: str, **tags):
        """Контекстный менеджер для измерения времени операции."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.record_metric(f"{operation_name}_duration", duration, tags)


def log_execution_time(logger: Optional[ContextualLogger] = None):
    """Декоратор для логирования времени выполнения функции."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            func_logger = logger or ContextualLogger(func.__module__)
            
            try:
                func_logger.info(f"Начинаем выполнение {func.__name__}")
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                func_logger.info(f"Завершено {func.__name__} за {duration:.2f}с")
                return result
            except Exception as e:
                duration = time.time() - start_time
                func_logger.error(f"Ошибка в {func.__name__} после {duration:.2f}с: {e}")
                raise
                
        return wrapper
    return decorator


def log_api_call(logger: Optional[ContextualLogger] = None):
    """Декоратор для логирования API вызовов."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_logger = logger or ContextualLogger(func.__module__)
            
            # Извлекаем URL из аргументов если возможно
            url = "unknown"
            if args and hasattr(args[0], 'url'):
                url = args[0].url
            elif 'url' in kwargs:
                url = kwargs['url']
                
            api_logger.set_context(api_url=url, function=func.__name__)
            
            try:
                api_logger.info("API запрос начат")
                result = func(*args, **kwargs)
                api_logger.info("API запрос успешен")
                return result
            except Exception as e:
                api_logger.error(f"API запрос неуспешен: {e}")
                raise
            finally:
                api_logger.clear_context()
                
        return wrapper
    return decorator


class StructuredLogger:
    """Структурированный логгер для JSON логов."""
    
    def __init__(self, name: str, output_file: Optional[Path] = None):
        self.name = name
        self.output_file = output_file or Path("logs/structured.jsonl")
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
    def log_event(self, event_type: str, message: str, **data):
        """Логирует структурированное событие."""
        log_entry = {
            "timestamp": time.time(),
            "logger": self.name,
            "event_type": event_type,
            "message": message,
            **data
        }
        
        try:
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logging.error(f"Не удалось записать структурированный лог: {e}")


# Глобальные экземпляры
metrics_logger = MetricsLogger()
structured_logger = StructuredLogger("epg_collector")


def setup_enhanced_logging(level: str = "INFO", enable_metrics: bool = True):
    """Настраивает улучшенную систему логирования."""
    from .logging_config import setup_logging
    
    # Базовая настройка
    setup_logging(level)
    
    # Добавляем обработчик для структурированных логов
    if enable_metrics:
        logger = logging.getLogger()
        
        class StructuredHandler(logging.Handler):
            def emit(self, record):
                structured_logger.log_event(
                    event_type="log",
                    message=record.getMessage(),
                    level=record.levelname,
                    module=record.module,
                    function=record.funcName,
                    line=record.lineno
                )
                
        structured_handler = StructuredHandler()
        structured_handler.setLevel(logging.WARNING)  # Только важные события
        logger.addHandler(structured_handler)
