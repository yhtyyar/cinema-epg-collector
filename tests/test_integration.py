"""
Интеграционные тесты для API cinema-epg-collector
"""
import pytest
import requests
import time
from typing import Dict, Any

# Базовый URL для тестирования
BASE_URL = "http://localhost:8000/api"

class TestAPIIntegration:
    """Интеграционные тесты для API"""
    
    @classmethod
    def setup_class(cls):
        """Ожидание готовности API перед тестами"""
        max_retries = 30
        for _ in range(max_retries):
            try:
                response = requests.get(f"{BASE_URL}/health", timeout=5)
                if response.status_code == 200:
                    break
            except requests.RequestException:
                pass
            time.sleep(1)
        else:
            pytest.fail("API не готов к тестированию")
    
    def test_health_endpoint(self):
        """Тест health check эндпоинта"""
        response = requests.get(f"{BASE_URL}/health")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json; charset=utf-8"
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "cinema-epg-collector-api"
    
    def test_movies_endpoint_basic(self):
        """Тест базового получения фильмов"""
        response = requests.get(f"{BASE_URL}/movies")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json; charset=utf-8"
        
        data = response.json()
        assert "movies" in data
        assert "pagination" in data
        assert isinstance(data["movies"], list)
        
        # Проверка структуры пагинации
        pagination = data["pagination"]
        assert "page" in pagination
        assert "per_page" in pagination
        assert "total" in pagination
        assert "pages" in pagination
    
    def test_movies_endpoint_with_pagination(self):
        """Тест пагинации фильмов"""
        response = requests.get(f"{BASE_URL}/movies?page=1&per_page=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["movies"]) <= 5
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["per_page"] == 5
    
    def test_movies_endpoint_with_search(self):
        """Тест поиска фильмов"""
        response = requests.get(f"{BASE_URL}/movies?q=test")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "movies" in data
        assert "pagination" in data
    
    def test_movies_endpoint_with_filters(self):
        """Тест фильтрации фильмов"""
        response = requests.get(f"{BASE_URL}/movies?year=2023&rating_gte=7.0")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "movies" in data
        assert "pagination" in data
    
    def test_channels_endpoint(self):
        """Тест получения каналов"""
        response = requests.get(f"{BASE_URL}/channels")
        
        assert response.status_code == 200
        assert response.headers.get("content-type") == "application/json; charset=utf-8"
        
        data = response.json()
        assert "movies" in data
        assert "cartoons" in data
        assert "total" in data
        assert isinstance(data["movies"], list)
        assert isinstance(data["cartoons"], list)
        assert isinstance(data["total"], int)
    
    def test_genres_endpoint(self):
        """Тест получения жанров"""
        response = requests.get(f"{BASE_URL}/genres")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "genres" in data
        assert isinstance(data["genres"], list)
    
    def test_invalid_endpoint(self):
        """Тест несуществующего эндпоинта"""
        response = requests.get(f"{BASE_URL}/nonexistent")
        
        assert response.status_code == 404
    
    def test_invalid_movie_id(self):
        """Тест получения несуществующего фильма"""
        response = requests.get(f"{BASE_URL}/movies/nonexistent_id")
        
        assert response.status_code == 404
    
    def test_movies_endpoint_invalid_params(self):
        """Тест некорректных параметров"""
        # Некорректная страница
        response = requests.get(f"{BASE_URL}/movies?page=0")
        assert response.status_code in [400, 422]  # Может быть 400 или 422
        
        # Некорректный per_page
        response = requests.get(f"{BASE_URL}/movies?per_page=0")
        assert response.status_code in [400, 422]
        
        # Некорректный рейтинг
        response = requests.get(f"{BASE_URL}/movies?rating_gte=15")
        assert response.status_code in [400, 422]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
