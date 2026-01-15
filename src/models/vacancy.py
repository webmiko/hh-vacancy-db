"""Модель данных для вакансии.

Модуль содержит класс Vacancy для представления данных о вакансии
и преобразования данных из API hh.ru в формат для базы данных.
"""

# 1. Импорты стандартной библиотеки
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

# 2. Импорты сторонних библиотек
# (нет сторонних импортов)

# 3. Импорты из проекта
# (нет локальных импортов)

# 4. Константы модуля
# (нет констант)


# 5. Приватные функции
def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
    """
    Парсит строку с датой в формате ISO 8601 в объект datetime.

    Args:
        date_str: Строка с датой в формате ISO 8601 или None

    Returns:
        Объект datetime или None
    """
    if not date_str:
        return None

    try:
        # Пробуем разные форматы даты из API hh.ru
        # Формат: "2024-01-15T10:00:00+0300" или "2024-01-15T10:00:00"
        if "+" in date_str or date_str.endswith("Z"):
            # С ISO форматом с временной зоной
            return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        else:
            # Без временной зоны
            return datetime.fromisoformat(date_str)
    except (ValueError, AttributeError):
        return None


# 6. Публичные классы
class Vacancy:
    """Класс для представления данных о вакансии.

    Предоставляет методы для создания объекта из данных API hh.ru
    и преобразования в формат для вставки в базу данных.

    Attributes:
        vacancy_id: Идентификатор вакансии из hh.ru
        employer_id: Идентификатор работодателя
        name: Название вакансии
        url: Ссылка на вакансию
        salary_from: Зарплата от
        salary_to: Зарплата до
        currency: Валюта зарплаты
        requirement: Требования к кандидату
        responsibility: Обязанности
        published_at: Дата публикации
    """

    def __init__(
        self,
        vacancy_id: int,
        employer_id: int,
        name: str,
        url: Optional[str] = None,
        salary_from: Optional[int] = None,
        salary_to: Optional[int] = None,
        currency: Optional[str] = None,
        requirement: Optional[str] = None,
        responsibility: Optional[str] = None,
        published_at: Optional[datetime] = None,
    ) -> None:
        """
        Инициализирует экземпляр класса Vacancy.

        Args:
            vacancy_id: Идентификатор вакансии из hh.ru
            employer_id: Идентификатор работодателя
            name: Название вакансии
            url: Ссылка на вакансию
            salary_from: Зарплата от
            salary_to: Зарплата до
            currency: Валюта зарплаты
            requirement: Требования к кандидату
            responsibility: Обязанности
            published_at: Дата публикации
        """
        self.vacancy_id = vacancy_id
        self.employer_id = employer_id
        self.name = name
        self.url = url
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.currency = currency
        self.requirement = requirement
        self.responsibility = responsibility
        self.published_at = published_at

    @classmethod
    def from_api_data(cls, data: Dict[str, Any], employer_id: Optional[int] = None) -> "Vacancy":
        """
        Создает объект Vacancy из данных API hh.ru.

        Args:
            data: Словарь с данными вакансии из API hh.ru
            employer_id: Идентификатор работодателя (если не указан в data)

        Returns:
            Объект Vacancy

        Example:
            >>> api_data = {"id": "123456", "name": "Python Developer", ...}
            >>> vacancy = Vacancy.from_api_data(api_data, employer_id=1455)
            >>> print(vacancy.name)
            Python Developer
        """
        vacancy_id = int(data.get("id", 0))

        # Получаем employer_id из данных или из параметра
        if employer_id is None:
            employer_obj = data.get("employer")
            if isinstance(employer_obj, dict):
                employer_id = int(employer_obj.get("id", 0))
            else:
                employer_id = 0

        name = data.get("name", "")
        url = data.get("alternate_url") or data.get("url")

        # Обрабатываем зарплату
        salary = data.get("salary")
        salary_from = None
        salary_to = None
        currency = None

        if isinstance(salary, dict):
            salary_from = salary.get("from")
            salary_to = salary.get("to")
            currency = salary.get("currency")

        # Обрабатываем требования и обязанности
        snippet = data.get("snippet", {})
        requirement = None
        responsibility = None

        if isinstance(snippet, dict):
            requirement = snippet.get("requirement")
            responsibility = snippet.get("responsibility")

        # Если нет в snippet, пробуем получить из description
        if not requirement and not responsibility:
            description = data.get("description")
            if description:
                # Простое разделение (в реальности может быть сложнее)
                requirement = description

        # Обрабатываем дату публикации
        published_at_str = data.get("published_at") or data.get("created_at")
        published_at = _parse_datetime(published_at_str)

        return cls(
            vacancy_id=vacancy_id,
            employer_id=employer_id,
            name=name,
            url=url,
            salary_from=salary_from,
            salary_to=salary_to,
            currency=currency,
            requirement=requirement,
            responsibility=responsibility,
            published_at=published_at,
        )

    def to_db_tuple(
        self,
    ) -> Tuple[
        int,
        int,
        str,
        Optional[str],
        Optional[int],
        Optional[int],
        Optional[str],
        Optional[str],
        Optional[str],
        Optional[datetime],
    ]:
        """
        Преобразует объект Vacancy в кортеж для вставки в базу данных.

        Returns:
            Кортеж с данными в порядке полей таблицы vacancies:
            (vacancy_id, employer_id, name, url, salary_from, salary_to,
             currency, requirement, responsibility, published_at)

        Example:
            >>> vacancy = Vacancy(123456, 1455, "Python Developer")
            >>> data = vacancy.to_db_tuple()
            >>> print(data[0])
            123456
        """
        return (
            self.vacancy_id,
            self.employer_id,
            self.name,
            self.url,
            self.salary_from,
            self.salary_to,
            self.currency,
            self.requirement,
            self.responsibility,
            self.published_at,
        )

    def __repr__(self) -> str:
        """
        Возвращает строковое представление объекта Vacancy.

        Returns:
            Строковое представление объекта
        """
        salary_str = f"{self.salary_from}-{self.salary_to}" if self.salary_from or self.salary_to else "не указана"
        return (
            f"Vacancy(vacancy_id={self.vacancy_id}, "
            f"employer_id={self.employer_id}, "
            f"name='{self.name}', "
            f"salary={salary_str} {self.currency or ''})"
        )
