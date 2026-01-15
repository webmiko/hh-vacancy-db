"""Тесты для модуля db_creator."""

# 1. Импорты стандартной библиотеки
import os
from unittest.mock import Mock, patch

# 2. Импорты сторонних библиотек
import pytest
import psycopg2

# 3. Импорты из проекта
from src.database.db_creator import DBCreator

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


# 6. Тесты для DBCreator
class TestDBCreator:
    """Тесты для класса DBCreator."""

    @patch.dict("os.environ", {}, clear=True)
    def test_init(self) -> None:
        """Тест инициализации класса DBCreator."""
        creator = DBCreator()
        assert creator.host == "localhost"
        assert creator.port == 5432
        assert creator.database == "hh_vacancies"
        assert creator.user == "postgres"
        assert creator.password == ""

    def test_init_with_params(self) -> None:
        """Тест инициализации с параметрами."""
        creator = DBCreator(
            host="test_host",
            port=5433,
            database="test_db",
            user="test_user",
            password="test_pass",
        )
        assert creator.host == "test_host"
        assert creator.port == 5433
        assert creator.database == "test_db"
        assert creator.user == "test_user"
        assert creator.password == "test_pass"

    @patch("src.database.db_creator.psycopg2.connect")
    def test_get_connection_to_postgres(self, mock_connect: Mock, mock_connection: Mock) -> None:
        """Тест подключения к серверу PostgreSQL."""
        mock_connect.return_value = mock_connection
        mock_connection.set_isolation_level = Mock()

        creator = DBCreator()
        conn = creator._get_connection_to_postgres()

        assert conn == mock_connection
        mock_connect.assert_called_once()
        mock_connection.set_isolation_level.assert_called_once()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_get_connection_to_database(self, mock_connect: Mock, mock_connection: Mock) -> None:
        """Тест подключения к целевой базе данных."""
        mock_connect.return_value = mock_connection

        creator = DBCreator()
        conn = creator._get_connection_to_database()

        assert conn == mock_connection
        mock_connect.assert_called_once()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_get_connection_to_postgres_error(self, mock_connect: Mock) -> None:
        """Тест обработки ошибки подключения к PostgreSQL."""
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        creator = DBCreator()
        with pytest.raises(psycopg2.Error):
            creator._get_connection_to_postgres()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_get_connection_to_database_error(self, mock_connect: Mock) -> None:
        """Тест обработки ошибки подключения к базе данных."""
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        creator = DBCreator()
        with pytest.raises(psycopg2.Error):
            creator._get_connection_to_database()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_create_database_exists(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест создания БД, когда она уже существует."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (True,)

        creator = DBCreator()
        creator.create_database()

        mock_cursor.execute.assert_called()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_create_database_new(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест создания новой БД."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        creator = DBCreator()
        creator.create_database()

        assert mock_cursor.execute.call_count >= 2
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_create_tables(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест создания таблиц."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        creator = DBCreator()
        creator.create_tables()

        assert mock_cursor.execute.call_count > 0
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_create_tables_error(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест обработки ошибки при создании таблиц."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Table creation failed")

        creator = DBCreator()
        with pytest.raises(psycopg2.Error):
            creator.create_tables()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_drop_tables(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест удаления таблиц."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor

        creator = DBCreator()
        creator.drop_tables()

        assert mock_cursor.execute.call_count > 0
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_database_exists(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест проверки существования БД."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (True,)

        creator = DBCreator()
        result = creator.database_exists()

        assert result is True
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_database_not_exists(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест проверки несуществующей БД."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None

        creator = DBCreator()
        result = creator.database_exists()

        assert result is False

    @patch("src.database.db_creator.psycopg2.connect")
    def test_tables_exist(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест проверки существования таблиц."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (2,)

        creator = DBCreator()
        result = creator.tables_exist()

        assert result is True

    @patch("src.database.db_creator.psycopg2.connect")
    def test_tables_not_exist(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест проверки несуществующих таблиц."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = (0,)

        creator = DBCreator()
        result = creator.tables_exist()

        assert result is False

    @patch("src.database.db_creator.psycopg2.connect")
    def test_tables_exist_error(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест обработки ошибки при проверке таблиц."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Query failed")

        creator = DBCreator()
        result = creator.tables_exist()

        assert result is False

    @patch("src.database.db_creator.psycopg2.connect")
    def test_create_database_error(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест обработки ошибки при создании БД."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Database creation failed")

        creator = DBCreator()
        with pytest.raises(psycopg2.Error):
            creator.create_database()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_drop_tables_error(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест обработки ошибки при удалении таблиц."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Drop failed")

        creator = DBCreator()
        with pytest.raises(psycopg2.Error):
            creator.drop_tables()

    @patch("src.database.db_creator.psycopg2.connect")
    def test_database_exists_error(self, mock_connect: Mock, mock_connection: Mock, mock_cursor: Mock) -> None:
        """Тест обработки ошибки при проверке существования БД."""
        mock_connect.return_value = mock_connection
        mock_connection.cursor.return_value = mock_cursor
        mock_cursor.execute.side_effect = psycopg2.Error("Query failed")

        creator = DBCreator()
        result = creator.database_exists()

        assert result is False
