"""Общие фикстуры для всех тестов проекта."""

# 1. Импорты стандартной библиотеки
from typing import Any, Dict
from unittest.mock import Mock, MagicMock

# 2. Импорты сторонних библиотек
import pytest

# 3. Импорты из проекта
# (нет импортов из проекта)

# 4. Константы модуля
# (нет констант)


# 5. Фикстуры для моков базы данных
@pytest.fixture
def mock_connection() -> Mock:
    """Фикстура для мока подключения к БД."""
    conn = Mock()
    conn.cursor = Mock()
    conn.close = Mock()
    conn.commit = Mock()
    conn.rollback = Mock()
    return conn


@pytest.fixture
def mock_cursor() -> Mock:
    """Фикстура для мока курсора."""
    cursor = Mock()
    cursor.execute = Mock()
    cursor.fetchone = Mock()
    cursor.fetchall = Mock()
    cursor.close = Mock()
    return cursor


# Примечание: mock_connect не выносится в фикстуру, так как тесты используют
# @patch декораторы для мокирования psycopg2.connect в каждом тесте отдельно


# 6. Фикстуры для тестовых данных API
@pytest.fixture
def sample_employer_data() -> Dict[str, Any]:
    """Фикстура с примером данных работодателя из API (базовая версия)."""
    return {
        "id": "1455",
        "name": "HeadHunter",
        "url": "https://api.hh.ru/employers/1455",
        "alternate_url": "http://hh.ru/employer/1455",
        "open_vacancies": 42,
    }


@pytest.fixture
def sample_employer_data_full() -> Dict[str, Any]:
    """Фикстура с полными данными работодателя из API."""
    return {
        "id": "1455",
        "name": "HeadHunter",
        "url": "https://api.hh.ru/employers/1455",
        "alternate_url": "http://hh.ru/employer/1455",
        "open_vacancies": 42,
        "vacancies_url": "https://api.hh.ru/vacancies?employer_id=1455",
        "trusted": True,
        "type": "company",
        "site_url": "http://hh.ru",
    }


@pytest.fixture
def sample_vacancy_data() -> Dict[str, Any]:
    """Фикстура с примером данных вакансии из API (базовая версия)."""
    return {
        "id": "123456",
        "name": "Python Developer",
        "alternate_url": "https://hh.ru/vacancy/123456",
        "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
        "employer": {"id": "1455"},
        "published_at": "2024-01-15T10:00:00+0300",
    }


@pytest.fixture
def sample_vacancy_data_full() -> Dict[str, Any]:
    """Фикстура с полными данными вакансии из API."""
    return {
        "id": "123456",
        "name": "Python Developer",
        "alternate_url": "https://hh.ru/vacancy/123456",
        "url": "https://api.hh.ru/vacancies/123456",
        "salary": {"from": 100000, "to": 150000, "currency": "RUR", "gross": False},
        "snippet": {
            "requirement": "Опыт работы от 3 лет. Знание Python, Django.",
            "responsibility": "Разработка веб-приложений. Участие в проектах.",
        },
        "employer": {
            "id": "1455",
            "name": "HeadHunter",
            "url": "https://api.hh.ru/employers/1455",
        },
        "published_at": "2024-01-15T10:00:00+0300",
    }


@pytest.fixture
def sample_vacancies_response() -> Dict[str, Any]:
    """Фикстура с примером ответа API для списка вакансий."""
    return {
        "items": [
            {
                "id": "123456",
                "name": "Python Developer",
                "alternate_url": "https://hh.ru/vacancy/123456",
                "salary": {"from": 100000, "to": 150000, "currency": "RUR"},
            },
            {
                "id": "123457",
                "name": "Backend Developer",
                "alternate_url": "https://hh.ru/vacancy/123457",
                "salary": {"from": 120000, "to": 180000, "currency": "RUR"},
            },
        ],
        "pages": 1,
        "per_page": 100,
        "page": 0,
        "found": 2,
    }


@pytest.fixture
def sample_company_data() -> Dict[str, Any]:
    """Фикстура с примером данных компании для модели Company."""
    return {
        "id": "1455",
        "name": "HeadHunter",
        "url": "https://api.hh.ru/employers/1455",
        "alternate_url": "http://hh.ru/employer/1455",
        "open_vacancies": 42,
        "description": "Крупная IT-компания",
        "area": {"id": "1", "name": "Москва"},
    }
