"""Тесты для модуля работы с API hh.ru."""

# 1. Импорты стандартной библиотеки
from typing import Any, Dict
from unittest.mock import Mock, patch

# 2. Импорты сторонних библиотек
import pytest
import requests

# 3. Импорты из проекта
from src.api.hh_api import HeadHunterAPI

# 4. Константы модуля
# (нет констант)


# 5. Тестовые данные
# (общие фикстуры определены в conftest.py)
# Для этого модуля используются sample_employer_data_full, sample_vacancy_data_full,
# sample_vacancies_response из conftest.py

# 6. Тесты
class TestHeadHunterAPI:
    """Тесты для класса HeadHunterAPI."""

    def test_init(self) -> None:
        """Тест инициализации класса HeadHunterAPI."""
        api = HeadHunterAPI()
        assert api._base_url == "https://api.hh.ru"
        assert "User-Agent" in api._headers

    @patch("src.api.hh_api.requests.get")
    def test_get_employer_success(self, mock_get: Mock, sample_employer_data_full: Dict[str, Any]) -> None:
        """Тест успешного получения данных о работодателе."""
        # Настройка мока
        mock_response = Mock()
        mock_response.json.return_value = sample_employer_data_full
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
    def test_get_vacancies_success(self, mock_get: Mock, sample_vacancies_response: Dict[str, Any]) -> None:
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
        sample_employer_data_full: Dict[str, Any],
        sample_vacancies_response: Dict[str, Any],
    ) -> None:
        """Тест успешного получения полных данных о работодателе и вакансиях."""
        # Настройка моков для двух запросов
        mock_responses = [
            Mock(),  # Для get_employer
            Mock(),  # Для get_vacancies
        ]
        mock_responses[0].json.return_value = sample_employer_data_full
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

    @patch("src.api.hh_api.requests.get")
    def test_get_employer_request_exception(self, mock_get: Mock) -> None:
        """Тест обработки RequestException при получении работодателя."""
        mock_get.side_effect = requests.RequestException("Connection error")

        api = HeadHunterAPI()
        result = api.get_employer(1455)

        assert result is None

    @patch("src.api.hh_api.requests.get")
    def test_get_employer_value_error(self, mock_get: Mock) -> None:
        """Тест обработки ValueError при парсинге JSON."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        result = api.get_employer(1455)

        assert result is None

    @patch("src.api.hh_api.requests.get")
    def test_get_employer_http_error_500(self, mock_get: Mock) -> None:
        """Тест обработки HTTP ошибки 500."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        result = api.get_employer(1455)

        assert result is None

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_pagination(self, mock_get: Mock) -> None:
        """Тест пагинации при получении вакансий."""
        # Первая страница
        page1_response = Mock()
        page1_response.json.return_value = {
            "items": [{"id": "1", "name": "Vacancy 1"}],
            "pages": 2,
            "per_page": 100,
            "page": 0,
            "found": 2,
        }
        page1_response.raise_for_status = Mock()

        # Вторая страница
        page2_response = Mock()
        page2_response.json.return_value = {
            "items": [{"id": "2", "name": "Vacancy 2"}],
            "pages": 2,
            "per_page": 100,
            "page": 1,
            "found": 2,
        }
        page2_response.raise_for_status = Mock()

        mock_get.side_effect = [page1_response, page2_response]

        api = HeadHunterAPI()
        result = api.get_vacancies(1455)

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_no_items_key(self, mock_get: Mock) -> None:
        """Тест обработки ответа без ключа items."""
        mock_response = Mock()
        mock_response.json.return_value = {"pages": 1, "per_page": 100, "page": 0, "found": 0}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        result = api.get_vacancies(1455)

        assert result == []

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_items_not_list(self, mock_get: Mock) -> None:
        """Тест обработки случая, когда items не является списком."""
        mock_response = Mock()
        mock_response.json.return_value = {"items": "not a list", "pages": 1}
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        result = api.get_vacancies(1455)

        assert result == []

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_json_error(self, mock_get: Mock) -> None:
        """Тест обработки ошибки парсинга JSON при получении вакансий."""
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        result = api.get_vacancies(1455)

        assert result == []

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_key_error(self, mock_get: Mock) -> None:
        """Тест обработки KeyError при получении вакансий."""
        mock_response = Mock()
        mock_response.json.side_effect = KeyError("missing_key")
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        result = api.get_vacancies(1455)

        assert result == []

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_exception(self, mock_get: Mock) -> None:
        """Тест обработки общего Exception при получении вакансий."""
        mock_get.side_effect = Exception("Unexpected error")

        api = HeadHunterAPI()
        result = api.get_vacancies(1455)

        assert result == []

    @patch("src.api.hh_api.requests.get")
    def test_get_employer_exception(self, mock_get: Mock) -> None:
        """Тест обработки общего Exception при получении работодателя."""
        mock_get.side_effect = Exception("Unexpected error")

        api = HeadHunterAPI()
        result = api.get_employer(1455)

        assert result is None

    @patch("src.api.hh_api.requests.get")
    def test_get_vacancies_http_error_500(self, mock_get: Mock) -> None:
        """Тест обработки HTTP ошибки 500 при получении вакансий."""
        import requests

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        api = HeadHunterAPI()
        result = api.get_vacancies(1455)

        assert result == []
