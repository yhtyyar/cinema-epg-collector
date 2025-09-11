#!/usr/bin/env python3
"""
Тест для проверки конфигурации API и логики пропуска обогащения.
"""

import os
import json
from pathlib import Path
from epg_collector.config import load_config
from epg_collector.data_validator import should_run_pipeline, get_data_status

def test_config_loading():
    """Тест загрузки конфигурации."""
    print("Тест загрузки конфигурации...")
    
    # Загружаем конфигурацию
    config = load_config()
    
    # Проверяем значения по умолчанию
    assert config.api_host == "0.0.0.0", f"Ожидался хост 0.0.0.0, получено {config.api_host}"
    assert config.api_port == 8000, f"Ожидался порт 8000, получено {config.api_port}"
    assert config.skip_enrichment_if_exists == True, f"Ожидалось SKIP_ENRICHMENT_IF_EXISTS=true, получено {config.skip_enrichment_if_exists}"
    
    print("✓ Конфигурация загружена корректно")

def test_data_validation():
    """Тест валидации данных."""
    print("Тест валидации данных...")
    
    # Создаем тестовую структуру данных
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    enriched_path = data_dir / "enriched_movies.json"
    
    # Тест 1: Нет данных
    if enriched_path.exists():
        enriched_path.unlink()
    
    should_run, reason = should_run_pipeline(skip_if_exists=True)
    assert should_run == True, f"Ожидалось should_run=True когда данных нет, получено {should_run}"
    print("✓ Корректно определяет необходимость запуска когда данных нет")
    
    # Тест 2: Данные существуют
    test_data = [{"id": "1", "title": "Test Movie"}]
    enriched_path.write_text(json.dumps(test_data), encoding="utf-8")
    
    should_run, reason = should_run_pipeline(skip_if_exists=True)
    assert should_run == False, f"Ожидалось should_run=False когда данные существуют, получено {should_run}"
    print("✓ Корректно определяет необходимость пропуска когда данные существуют")
    
    # Тест 3: Принудительный запуск
    should_run, reason = should_run_pipeline(force_run=True, skip_if_exists=True)
    assert should_run == True, f"Ожидалось should_run=True при принудительном запуске, получено {should_run}"
    print("✓ Корректно игнорирует skip_if_exists при принудительном запуске")
    
    # Очищаем тестовые данные
    if enriched_path.exists():
        enriched_path.unlink()
    
    print("✓ Валидация данных работает корректно")

def main():
    """Основная функция тестирования."""
    print("Запуск тестов конфигурации API...")
    
    try:
        test_config_loading()
        test_data_validation()
        print("\n✅ Все тесты пройдены успешно!")
    except Exception as e:
        print(f"\n❌ Тесты провалены: {e}")
        raise

if __name__ == "__main__":
    main()