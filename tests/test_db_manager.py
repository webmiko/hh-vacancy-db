"""Тесты для модуля db_manager."""

# 1. Импорты стандартной библиотеки
import os
from unittest.mock import Mock, MagicMock, patch

# 2. Импорты сторонних библиотек
import pytest
import psycopg2

# 3. Импорты из проекта
from src.database.db_manager import DBManager

# 4. Константы модуля
# (нет констант)


# 5. Тестовые данные
@pytest.fixture
def mock_connection() -> Mock:
    """Фикстура для мока подключения к БД."""
    conn = Mock()
    conn.cursor = Mock()
    conn.close = Mock()
    conn.commit = Mock()
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


# 6. Тесты для DBManager
class TestDBManager:
    """Тесты для класса DBManager."""

    @patch.dict("os.environ", {}, clear=True)
    def test_init(self) -> None:
        """Тест инициализации класса DBManager."""
        manager = DBManager()
        assert manager.host == "localhost"
        assert manager.port == 5432
        assert manager.database == "hh_vacancies"
        assert manager.user == "postgres"
        assert manager.password == ""

    def test_init_with_params(self) -> None:
        """Тест инициализации с параметрами."""
        manager = DBManager(
            host="test_host",
            port=5433,
            database="test_db",
            user="test_user",
            password="test_pass",
        )
        assert manager.host == "test_host"
        assert manager.port == 5433
        assert manager.database == "test_db"
        assert manager.user == "test_user"
        assert manager.password == "test_pass"

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_connection(self, mock_connect: Mock, mock_connection: Mock) -> None:
        """Тест подключения к базе данных."""
        mock_connect.return_value = mock_connection

        manager = DBManager()
        conn = manager._get_connection()

        assert conn == mock_connection
        mock_connect.assert_called_once()

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_connection_error(self, mock_connect: Mock) -> None:
        """Тест обработки ошибки подключения."""
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        manager = DBManager()
        with pytest.raises(psycopg2.Error):
            manager._get_connection()

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_companies_and_vacancies_count(
        self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock
    ) -> None:
        """Тест получения списка компаний и количества вакансий."""
        from psycopg2.extras import RealDictRow

        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        # Создаем мок для RealDictRow
        row1 = MagicMock(spec=RealDictRow)
        row1.__getitem__ = Mock(side_effect=lambda key: {"name": "Company1", "vacancies_count": 5}[key])
        row1.keys = Mock(return_value=["name", "vacancies_count"])

        row2 = MagicMock(spec=RealDictRow)
        row2.__getitem__ = Mock(side_effect=lambda key: {"name": "Company2", "vacancies_count": 3}[key])
        row2.keys = Mock(return_value=["name", "vacancies_count"])

        mock_cursor.fetchall.return_value = [row1, row2]

        manager = DBManager()
        result = manager.get_companies_and_vacancies_count()

        assert len(result) == 2
        mock_cursor.execute.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_companies_and_vacancies_count_error(
        self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock
    ) -> None:
        """Тест обработки ошибки при получении компаний."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Query failed")

        manager = DBManager()
        with pytest.raises(psycopg2.Error):
            manager.get_companies_and_vacancies_count()

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_all_vacancies(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест получения всех вакансий."""
        from psycopg2.extras import RealDictRow

        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        row = MagicMock(spec=RealDictRow)
        row.__getitem__ = Mock(
            side_effect=lambda key: {
                "company_name": "Company1",
                "name": "Vacancy1",
                "salary_from": 100000,
                "salary_to": 150000,
                "currency": "RUR",
                "url": "https://hh.ru/vacancy/1",
            }[key]
        )
        row.keys = Mock(return_value=["company_name", "name", "salary_from", "salary_to", "currency", "url"])

        mock_cursor.fetchall.return_value = [row]

        manager = DBManager()
        result = manager.get_all_vacancies()

        assert len(result) == 1
        mock_cursor.execute.assert_called_once()

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_avg_salary(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест получения средней зарплаты."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        # Обычный cursor возвращает кортеж, а не dict
        mock_cursor.fetchone.return_value = (125000.0,)

        manager = DBManager()
        result = manager.get_avg_salary()

        assert result == 125000.0
        mock_cursor.execute.assert_called_once()

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_avg_salary_none(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест получения средней зарплаты, когда данных нет."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        manager = DBManager()
        result = manager.get_avg_salary()

        assert result == 0.0

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_vacancies_with_higher_salary(
        self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock
    ) -> None:
        """Тест получения вакансий с зарплатой выше средней."""
        from psycopg2.extras import RealDictRow

        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        row = MagicMock(spec=RealDictRow)
        row.__getitem__ = Mock(
            side_effect=lambda key: {
                "name": "Vacancy1",
                "company_name": "Company1",
                "salary_from": 150000,
                "salary_to": 200000,
                "currency": "RUR",
                "url": "https://hh.ru/vacancy/1",
            }[key]
        )
        row.keys = Mock(return_value=["name", "company_name", "salary_from", "salary_to", "currency", "url"])

        mock_cursor.fetchall.return_value = [row]

        manager = DBManager()
        result = manager.get_vacancies_with_higher_salary()

        assert len(result) == 1
        mock_cursor.execute.assert_called_once()

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_vacancies_with_keyword(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест поиска вакансий по ключевому слову."""
        from psycopg2.extras import RealDictRow, RealDictCursor

        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        row = MagicMock(spec=RealDictRow)
        row.__getitem__ = Mock(
            side_effect=lambda key: {
                "name": "Python Developer",
                "vacancy_id": 123456,
                "employer_id": 1455,
                "salary_from": 100000,
                "salary_to": 150000,
                "currency": "RUR",
                "url": "https://hh.ru/vacancy/1",
            }[key]
        )
        row.keys = Mock(return_value=["name", "vacancy_id", "employer_id", "salary_from", "salary_to", "currency", "url"])

        mock_cursor.fetchall.return_value = [row]

        manager = DBManager()
        result = manager.get_vacancies_with_keyword("Python")

        assert len(result) == 1
        mock_cursor.execute.assert_called_once()

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_vacancies_with_keyword_empty(
        self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock
    ) -> None:
        """Тест поиска вакансий, когда ничего не найдено."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = []

        manager = DBManager()
        result = manager.get_vacancies_with_keyword("NonExistent")

        assert result == []

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_vacancies_with_keyword_empty_string(
        self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock
    ) -> None:
        """Тест поиска вакансий с пустой строкой."""
        manager = DBManager()
        result = manager.get_vacancies_with_keyword("")

        assert result == []

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_all_vacancies_error(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест обработки ошибки при получении всех вакансий."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Query failed")

        manager = DBManager()
        with pytest.raises(psycopg2.Error):
            manager.get_all_vacancies()

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_avg_salary_error(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест обработки ошибки при получении средней зарплаты."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Query failed")

        manager = DBManager()
        with pytest.raises(psycopg2.Error):
            manager.get_avg_salary()

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_vacancies_with_higher_salary_error(
        self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock
    ) -> None:
        """Тест обработки ошибки при получении вакансий с зарплатой выше средней."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Query failed")

        manager = DBManager()
        with pytest.raises(psycopg2.Error):
            manager.get_vacancies_with_higher_salary()

    @patch("src.database.db_manager.psycopg2.connect")
    def test_get_vacancies_with_keyword_error(
        self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock
    ) -> None:
        """Тест обработки ошибки при поиске вакансий."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Query failed")

        manager = DBManager()
        with pytest.raises(psycopg2.Error):
            manager.get_vacancies_with_keyword("Python")
