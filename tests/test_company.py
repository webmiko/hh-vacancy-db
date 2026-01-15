"""Тесты для модели Company."""

# 1. Импорты стандартной библиотеки
from typing import Any, Dict

# 2. Импорты сторонних библиотек
import pytest

# 3. Импорты из проекта
from src.models.company import Company

# 4. Константы модуля
# (нет констант)


# 5. Тестовые данные
@pytest.fixture
def sample_company_data() -> Dict[str, Any]:
    """Фикстура с примером данных компании из API."""
    return {
        "id": "1455",
        "name": "HeadHunter",
        "url": "https://api.hh.ru/employers/1455",
        "alternate_url": "http://hh.ru/employer/1455",
        "open_vacancies": 42,
        "description": "Крупная IT-компания",
        "area": {"id": "1", "name": "Москва"},
    }


# 6. Тесты для Company
class TestCompany:
    """Тесты для класса Company."""

    def test_init(self) -> None:
        """Тест инициализации класса Company."""
        company = Company(
            employer_id=1455,
            name="HeadHunter",
            url="https://hh.ru/employer/1455",
            description="IT-компания",
            area="Москва",
            open_vacancies=42,
        )
        assert company.employer_id == 1455
        assert company.name == "HeadHunter"
        assert company.url == "https://hh.ru/employer/1455"
        assert company.description == "IT-компания"
        assert company.area == "Москва"
        assert company.open_vacancies == 42

    def test_init_with_optional_none(self) -> None:
        """Тест инициализации с опциональными параметрами None."""
        company = Company(employer_id=1455, name="HeadHunter")
        assert company.employer_id == 1455
        assert company.name == "HeadHunter"
        assert company.url is None
        assert company.description is None
        assert company.area is None
        assert company.open_vacancies is None

    def test_from_api_data(self, sample_company_data: Dict[str, Any]) -> None:
        """Тест создания Company из данных API."""
        company = Company.from_api_data(sample_company_data)
        assert company.employer_id == 1455
        assert company.name == "HeadHunter"
        assert company.url == "http://hh.ru/employer/1455"
        assert company.description == "Крупная IT-компания"
        assert company.area == "Москва"
        assert company.open_vacancies == 42

    def test_from_api_data_with_alternate_url(self, sample_company_data: Dict[str, Any]) -> None:
        """Тест создания Company с alternate_url."""
        del sample_company_data["alternate_url"]
        company = Company.from_api_data(sample_company_data)
        assert company.url == "https://api.hh.ru/employers/1455"

    def test_from_api_data_with_string_area(self) -> None:
        """Тест создания Company с area как строкой."""
        data = {"id": "1455", "name": "HeadHunter", "area": "Москва"}
        company = Company.from_api_data(data)
        assert company.area == "Москва"

    def test_from_api_data_without_area(self) -> None:
        """Тест создания Company без area."""
        data = {"id": "1455", "name": "HeadHunter"}
        company = Company.from_api_data(data)
        assert company.area is None

    def test_to_db_tuple(self) -> None:
        """Тест преобразования Company в кортеж для БД."""
        company = Company(
            employer_id=1455,
            name="HeadHunter",
            url="https://hh.ru/employer/1455",
            description="IT-компания",
            area="Москва",
            open_vacancies=42,
        )
        result = company.to_db_tuple()
        assert result == (1455, "HeadHunter", "https://hh.ru/employer/1455", "IT-компания", "Москва", 42)

    def test_to_db_tuple_with_none(self) -> None:
        """Тест преобразования Company в кортеж с None значениями."""
        company = Company(employer_id=1455, name="HeadHunter")
        result = company.to_db_tuple()
        assert result == (1455, "HeadHunter", None, None, None, None)

    def test_repr(self) -> None:
        """Тест строкового представления Company."""
        company = Company(
            employer_id=1455,
            name="HeadHunter",
            url="https://hh.ru/employer/1455",
            area="Москва",
            open_vacancies=42,
        )
        repr_str = repr(company)
        assert "Company" in repr_str
        assert "1455" in repr_str
        assert "HeadHunter" in repr_str
