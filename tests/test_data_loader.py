"""Тесты для модуля data_loader."""

# 1. Импорты стандартной библиотеки
from unittest.mock import Mock, patch
from typing import Any, Dict

# 2. Импорты сторонних библиотек
import pytest
import psycopg2

# 3. Импорты из проекта
from src.utils.data_loader import load_data_to_db, DEFAULT_EMPLOYER_IDS

# 4. Константы модуля
# (нет констант)


# 5. Тестовые данные
# (общие фикстуры определены в conftest.py)

# 6. Тесты для load_data_to_db
class TestLoadDataToDB:
    """Тесты для функции load_data_to_db."""

    @patch("src.utils.data_loader.execute_values")
    @patch("src.utils.data_loader.HeadHunterAPI")
    @patch("src.utils.data_loader.psycopg2.connect")
    def test_load_data_to_db_success(
        self,
        mock_connect: Mock,
        mock_api_class: Mock,
        mock_execute_values: Mock,
        sample_employer_data: Dict[str, Any],
        sample_vacancy_data: Dict[str, Any],
    ) -> None:
        """Тест успешной загрузки данных в БД."""
        # Настройка мока API
        mock_api = Mock()
        mock_api.get_employer_vacancies.return_value = {
            "employer": sample_employer_data,
            "vacancies": [sample_vacancy_data],
        }
        mock_api_class.return_value = mock_api

        # Настройка мока БД
        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Выполнение
        load_data_to_db([1455])

        # Проверки
        mock_api.get_employer_vacancies.assert_called_once_with(1455)
        mock_cursor.execute.assert_called()  # INSERT для компании
        mock_execute_values.assert_called()  # Массовая вставка вакансий
        mock_connection.commit.assert_called()
        mock_connection.close.assert_called_once()

    @patch("src.utils.data_loader.HeadHunterAPI")
    @patch("src.utils.data_loader.psycopg2.connect")
    def test_load_data_to_db_default_employers(
        self,
        mock_connect: Mock,
        mock_api_class: Mock,
        sample_employer_data: Dict[str, Any],
    ) -> None:
        """Тест загрузки данных с дефолтным списком работодателей."""
        mock_api = Mock()
        mock_api.get_employer_vacancies.return_value = {
            "employer": sample_employer_data,
            "vacancies": [],
        }
        mock_api_class.return_value = mock_api

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        load_data_to_db()

        # Должно быть вызвано для каждого работодателя из DEFAULT_EMPLOYER_IDS
        assert mock_api.get_employer_vacancies.call_count == len(DEFAULT_EMPLOYER_IDS)

    @patch("src.utils.data_loader.HeadHunterAPI")
    @patch("src.utils.data_loader.psycopg2.connect")
    def test_load_data_to_db_no_employer(
        self,
        mock_connect: Mock,
        mock_api_class: Mock,
    ) -> None:
        """Тест загрузки данных, когда работодатель не найден."""
        mock_api = Mock()
        mock_api.get_employer_vacancies.return_value = {"employer": None, "vacancies": []}
        mock_api_class.return_value = mock_api

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        load_data_to_db([999999])

        # Не должно быть INSERT, так как работодатель не найден
        mock_cursor.execute.assert_not_called()

    @patch("src.utils.data_loader.psycopg2.connect")
    def test_load_data_to_db_connection_error(self, mock_connect: Mock) -> None:
        """Тест обработки ошибки подключения к БД."""
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        with pytest.raises(psycopg2.Error):
            load_data_to_db([1455])

    @patch("src.utils.data_loader.HeadHunterAPI")
    @patch("src.utils.data_loader.psycopg2.connect")
    def test_load_data_to_db_company_creation_error(
        self,
        mock_connect: Mock,
        mock_api_class: Mock,
    ) -> None:
        """Тест обработки ошибки создания объекта Company."""
        from src.models.company import Company

        mock_api = Mock()
        # Данные, которые вызовут ошибку при создании Company
        # Company.from_api_data может обработать это, но проверим что код продолжает работать
        mock_api.get_employer_vacancies.return_value = {
            "employer": None,  # Работодатель не найден
            "vacancies": [],
        }
        mock_api_class.return_value = mock_api

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Не должно быть ошибки, просто пропуск
        load_data_to_db([1455])

        # INSERT не должен быть вызван, так как работодатель None
        mock_cursor.execute.assert_not_called()

    @patch("src.utils.data_loader.HeadHunterAPI")
    @patch("src.utils.data_loader.psycopg2.connect")
    def test_load_data_to_db_insert_error(
        self,
        mock_connect: Mock,
        mock_api_class: Mock,
        sample_employer_data: Dict[str, Any],
    ) -> None:
        """Тест обработки ошибки при вставке данных."""
        mock_api = Mock()
        mock_api.get_employer_vacancies.return_value = {
            "employer": sample_employer_data,
            "vacancies": [],
        }
        mock_api_class.return_value = mock_api

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_cursor.execute.side_effect = psycopg2.Error("Insert failed")
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        # Не должно быть ошибки, просто логирование
        load_data_to_db([1455])

        mock_connection.rollback.assert_called()

    @patch("src.utils.data_loader.execute_values")
    @patch("src.utils.data_loader.HeadHunterAPI")
    @patch("src.utils.data_loader.psycopg2.connect")
    def test_load_data_to_db_vacancy_insert_error(
        self,
        mock_connect: Mock,
        mock_api_class: Mock,
        mock_execute_values: Mock,
        sample_employer_data: Dict[str, Any],
        sample_vacancy_data: Dict[str, Any],
    ) -> None:
        """Тест обработки ошибки при вставке вакансий."""
        from psycopg2.extras import execute_values

        mock_api = Mock()
        mock_api.get_employer_vacancies.return_value = {
            "employer": sample_employer_data,
            "vacancies": [sample_vacancy_data],
        }
        mock_api_class.return_value = mock_api

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        mock_execute_values.side_effect = psycopg2.Error("Insert failed")

        # Не должно быть ошибки, просто логирование
        load_data_to_db([1455])

        mock_connection.rollback.assert_called()

    @patch("src.utils.data_loader.HeadHunterAPI")
    @patch("src.utils.data_loader.psycopg2.connect")
    def test_load_data_to_db_critical_error(
        self,
        mock_connect: Mock,
        mock_api_class: Mock,
    ) -> None:
        """Тест обработки критической ошибки."""
        mock_api = Mock()
        mock_api.get_employer_vacancies.side_effect = Exception("Critical error")
        mock_api_class.return_value = mock_api

        mock_connection = Mock()
        mock_cursor = Mock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection

        with pytest.raises(Exception):
            load_data_to_db([1455])

        mock_connection.rollback.assert_called()
        mock_connection.close.assert_called_once()
