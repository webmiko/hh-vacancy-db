"""Тесты для модели Vacancy."""

# 1. Импорты стандартной библиотеки
from datetime import datetime
from typing import Any, Dict

# 2. Импорты сторонних библиотек
import pytest

# 3. Импорты из проекта
from src.models.vacancy import Vacancy, _parse_datetime

# 4. Константы модуля
# (нет констант)


# 5. Тестовые данные
# (общие фикстуры определены в conftest.py)
# Для этого модуля используется sample_vacancy_data_full из conftest.py

# 6. Тесты для Vacancy
class TestVacancy:
    """Тесты для класса Vacancy."""

    def test_init(self) -> None:
        """Тест инициализации класса Vacancy."""
        published_at = datetime(2024, 1, 15, 10, 0, 0)
        vacancy = Vacancy(
            vacancy_id=123456,
            employer_id=1455,
            name="Python Developer",
            url="https://hh.ru/vacancy/123456",
            salary_from=100000,
            salary_to=150000,
            currency="RUR",
            requirement="Опыт работы от 3 лет",
            responsibility="Разработка веб-приложений",
            published_at=published_at,
        )
        assert vacancy.vacancy_id == 123456
        assert vacancy.employer_id == 1455
        assert vacancy.name == "Python Developer"
        assert vacancy.url == "https://hh.ru/vacancy/123456"
        assert vacancy.salary_from == 100000
        assert vacancy.salary_to == 150000
        assert vacancy.currency == "RUR"
        assert vacancy.requirement == "Опыт работы от 3 лет"
        assert vacancy.responsibility == "Разработка веб-приложений"
        assert vacancy.published_at == published_at

    def test_init_with_optional_none(self) -> None:
        """Тест инициализации с опциональными параметрами None."""
        vacancy = Vacancy(vacancy_id=123456, employer_id=1455, name="Python Developer")
        assert vacancy.vacancy_id == 123456
        assert vacancy.employer_id == 1455
        assert vacancy.name == "Python Developer"
        assert vacancy.url is None
        assert vacancy.salary_from is None
        assert vacancy.salary_to is None
        assert vacancy.currency is None
        assert vacancy.requirement is None
        assert vacancy.responsibility is None
        assert vacancy.published_at is None

    def test_from_api_data(self, sample_vacancy_data_full: Dict[str, Any]) -> None:
        """Тест создания Vacancy из данных API."""
        vacancy = Vacancy.from_api_data(sample_vacancy_data_full)
        assert vacancy.vacancy_id == 123456
        assert vacancy.employer_id == 1455
        assert vacancy.name == "Python Developer"
        assert vacancy.url == "https://hh.ru/vacancy/123456"
        assert vacancy.salary_from == 100000
        assert vacancy.salary_to == 150000
        assert vacancy.currency == "RUR"
        assert vacancy.requirement == "Опыт работы от 3 лет. Знание Python, Django."
        assert vacancy.responsibility == "Разработка веб-приложений. Участие в проектах."
        assert isinstance(vacancy.published_at, datetime)

    def test_from_api_data_without_salary(self) -> None:
        """Тест создания Vacancy без зарплаты."""
        data = {
            "id": "123456",
            "name": "Python Developer",
            "employer": {"id": "1455"},
            "published_at": "2024-01-15T10:00:00+0300",
        }
        vacancy = Vacancy.from_api_data(data)
        assert vacancy.salary_from is None
        assert vacancy.salary_to is None
        assert vacancy.currency is None

    def test_from_api_data_with_salary_from_only(self) -> None:
        """Тест создания Vacancy только с salary_from."""
        data = {
            "id": "123456",
            "name": "Python Developer",
            "employer": {"id": "1455"},
            "salary": {"from": 100000, "currency": "RUR"},
            "published_at": "2024-01-15T10:00:00+0300",
        }
        vacancy = Vacancy.from_api_data(data)
        assert vacancy.salary_from == 100000
        assert vacancy.salary_to is None
        assert vacancy.currency == "RUR"

    def test_from_api_data_with_salary_to_only(self) -> None:
        """Тест создания Vacancy только с salary_to."""
        data = {
            "id": "123456",
            "name": "Python Developer",
            "employer": {"id": "1455"},
            "salary": {"to": 150000, "currency": "RUR"},
            "published_at": "2024-01-15T10:00:00+0300",
        }
        vacancy = Vacancy.from_api_data(data)
        assert vacancy.salary_from is None
        assert vacancy.salary_to == 150000
        assert vacancy.currency == "RUR"

    def test_from_api_data_without_snippet(self) -> None:
        """Тест создания Vacancy без snippet."""
        data = {
            "id": "123456",
            "name": "Python Developer",
            "employer": {"id": "1455"},
            "published_at": "2024-01-15T10:00:00+0300",
        }
        vacancy = Vacancy.from_api_data(data)
        assert vacancy.requirement is None
        assert vacancy.responsibility is None

    def test_from_api_data_without_published_at(self) -> None:
        """Тест создания Vacancy без published_at."""
        data = {"id": "123456", "name": "Python Developer", "employer": {"id": "1455"}}
        vacancy = Vacancy.from_api_data(data)
        assert vacancy.published_at is None

    def test_to_db_tuple(self) -> None:
        """Тест преобразования Vacancy в кортеж для БД."""
        published_at = datetime(2024, 1, 15, 10, 0, 0)
        vacancy = Vacancy(
            vacancy_id=123456,
            employer_id=1455,
            name="Python Developer",
            url="https://hh.ru/vacancy/123456",
            salary_from=100000,
            salary_to=150000,
            currency="RUR",
            requirement="Опыт работы",
            responsibility="Разработка",
            published_at=published_at,
        )
        result = vacancy.to_db_tuple()
        assert result[0] == 123456
        assert result[1] == 1455
        assert result[2] == "Python Developer"
        assert result[3] == "https://hh.ru/vacancy/123456"
        assert result[4] == 100000
        assert result[5] == 150000
        assert result[6] == "RUR"
        assert result[7] == "Опыт работы"
        assert result[8] == "Разработка"
        assert result[9] == published_at

    def test_to_db_tuple_with_none(self) -> None:
        """Тест преобразования Vacancy в кортеж с None значениями."""
        vacancy = Vacancy(vacancy_id=123456, employer_id=1455, name="Python Developer")
        result = vacancy.to_db_tuple()
        assert result[0] == 123456
        assert result[1] == 1455
        assert result[2] == "Python Developer"
        assert result[3] is None
        assert result[4] is None
        assert result[5] is None
        assert result[6] is None
        assert result[7] is None
        assert result[8] is None
        assert result[9] is None

    def test_repr(self) -> None:
        """Тест строкового представления Vacancy."""
        vacancy = Vacancy(vacancy_id=123456, employer_id=1455, name="Python Developer")
        repr_str = repr(vacancy)
        assert "Vacancy" in repr_str
        assert "123456" in repr_str
        assert "Python Developer" in repr_str


# 7. Тесты для функции _parse_datetime
class TestParseDatetime:
    """Тесты для функции _parse_datetime."""

    def test_parse_datetime_with_timezone(self) -> None:
        """Тест парсинга даты с временной зоной."""
        date_str = "2024-01-15T10:00:00+0300"
        result = _parse_datetime(date_str)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_datetime_without_timezone(self) -> None:
        """Тест парсинга даты без временной зоны."""
        date_str = "2024-01-15T10:00:00"
        result = _parse_datetime(date_str)
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_parse_datetime_with_z(self) -> None:
        """Тест парсинга даты с Z (UTC)."""
        date_str = "2024-01-15T10:00:00Z"
        result = _parse_datetime(date_str)
        assert isinstance(result, datetime)

    def test_parse_datetime_none(self) -> None:
        """Тест парсинга None."""
        result = _parse_datetime(None)
        assert result is None

    def test_parse_datetime_empty_string(self) -> None:
        """Тест парсинга пустой строки."""
        result = _parse_datetime("")
        assert result is None

    def test_parse_datetime_invalid_format(self) -> None:
        """Тест парсинга невалидного формата."""
        result = _parse_datetime("invalid-date")
        assert result is None
