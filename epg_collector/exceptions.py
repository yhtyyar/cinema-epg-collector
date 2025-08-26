"""Пользовательские исключения для проекта."""
from __future__ import annotations


class EPGCollectorError(Exception):
    """Базовое исключение для EPG Collector."""
    pass


class ConfigurationError(EPGCollectorError):
    """Ошибка конфигурации."""
    pass


class APIError(EPGCollectorError):
    """Ошибка при работе с внешними API."""
    
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class DataProcessingError(EPGCollectorError):
    """Ошибка обработки данных."""
    pass


class EnrichmentError(EPGCollectorError):
    """Ошибка обогащения данных."""
    pass


class PosterDownloadError(EPGCollectorError):
    """Ошибка скачивания постера."""
    pass
