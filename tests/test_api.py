"""Тесты для модуля работы с API hh.ru."""

# 1. Импорты стандартной библиотеки
from unittest.mock import Mock, patch
from typing import Any, Dict

# 2. Импорты сторонних библиотек
import pytest
import requests

# 3. Импорты из проекта
from src.api.hh_api import HeadHunterAPI

# 4. Константы модуля
# (нет констант)


# 5. Тестовые данные
@pytest.fixture
def sample_employer_data() -> Dict[str, Any]:
    """Фикстура с примером данных работодателя из API."""
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
    """Фикстура с примером данных вакансии из API."""
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


# 6. Тесты
class TestHeadHunterAPI:
    """Тесты для класса HeadHunterAPI."""

    def test_init(self) -> None:
        """Тест инициализации класса HeadHunterAPI."""
        api = HeadHunterAPI()
        assert api._base_url == "https://api.hh.ru"
        assert "User-Agent" in api._headers

    @patch("src.api.hh_api.requests.get")
    def test_get_employer_success(self, mock_get: Mock, sample_employer_data: Dict[str, Any]) -> None:
        """Тест успешного получения данных о работодателе."""
        # Настройка мока
        mock_response = Mock()
        mock_response.json.return_value = sample_employer_data
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Выполнение
        api = HeadHunterAPI()
        result = api.get_employer(1455)

        # Проверки
        assert result is not None
        assert result["id"] == "1455"
        assert result["name"] == "HeadHunter"
        mock_get.assert_called_once()

    @patch("src.api.hh_api.requests.get")
    def test_get_employer_not_found(self, mock_get: Mock) -> None:
        """Тест обработки случая, когда работодатель не найден."""
        # Настройка мока для 404 ошибки
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        # Выполнение
        api = HeadHunterAPI()
        result = api.get_employer(999999)

        # Проверки
        assert result is None

    def test_get_employer_invalid_id(self) -> None:
        """Тест обработки некорректного ID работодателя."""
        api = HeadHunterAPI()
        assert api.get_employer(-1) is None
        assert api.get_employer(0) is None

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_success(
        self, mock_get: Mock, sample_vacancies_response: Dict[str, Any]
    ) -> None:
        """Тест успешного получения списка вакансий."""
        # Настройка мока
        mock_response = Mock()
        mock_response.json.return_value = sample_vacancies_response
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Выполнение
        api = HeadHunterAPI()
        result = api.get_vacancies(1455)

        # Проверки
        assert len(result) == 2
        assert result[0]["id"] == "123456"
        assert result[1]["id"] == "123457"

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_empty(self, mock_get: Mock) -> None:
        """Тест получения пустого списка вакансий."""
        # Настройка мока для пустого ответа
        mock_response = Mock()
        mock_response.json.return_value = {"items": [], "pages": 1, "per_page": 100, "page": 0, "found": 0}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # Выполнение
        api = HeadHunterAPI()
        result = api.get_vacancies(1455)

        # Проверки
        assert result == []

    def test_get_vacancies_invalid_id(self) -> None:
        """Тест обработки некорректного ID работодателя."""
        api = HeadHunterAPI()
        assert api.get_vacancies(-1) == []
        assert api.get_vacancies(0) == []

    @patch("src.api.hh_api.requests.get")
    def test_get_employer_vacancies_success(
        self,
        mock_get: Mock,
        sample_employer_data: Dict[str, Any],
        sample_vacancies_response: Dict[str, Any],
    ) -> None:
        """Тест успешного получения полных данных о работодателе и вакансиях."""
        # Настройка моков для двух запросов
        mock_responses = [
            Mock(),  # Для get_employer
            Mock(),  # Для get_vacancies
        ]
        mock_responses[0].json.return_value = sample_employer_data
        mock_responses[0].raise_for_status = Mock()
        mock_responses[1].json.return_value = sample_vacancies_response
        mock_responses[1].raise_for_status = Mock()
        mock_get.side_effect = mock_responses

        # Выполнение
        api = HeadHunterAPI()
        result = api.get_employer_vacancies(1455)

        # Проверки
        assert result["employer"] is not None
        assert result["employer"]["name"] == "HeadHunter"
        assert len(result["vacancies"]) == 2

    @patch("src.api.hh_api.requests.get")
    def test_get_employer_vacancies_employer_not_found(self, mock_get: Mock) -> None:
        """Тест обработки случая, когда работодатель не найден."""
        # Настройка мока для 404 ошибки
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        # Выполнение
        api = HeadHunterAPI()
        result = api.get_employer_vacancies(999999)

        # Проверки
        assert result["employer"] is None
        assert result["vacancies"] == []
