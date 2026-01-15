"""Модель данных для компании (работодателя).

Модуль содержит класс Company для представления данных о работодателе
и преобразования данных из API hh.ru в формат для базы данных.
"""

# 1. Импорты стандартной библиотеки
from typing import Any, Dict, Optional, Tuple

# 2. Импорты сторонних библиотек
# (нет сторонних импортов)

# 3. Импорты из проекта
# (нет локальных импортов)

# 4. Константы модуля
# (нет констант)


# 5. Публичные классы
class Company:
    """Класс для представления данных о компании (работодателе).

    Предоставляет методы для создания объекта из данных API hh.ru
    и преобразования в формат для вставки в базу данных.

    Attributes:
        employer_id: Идентификатор работодателя из hh.ru
        name: Название компании
        url: Ссылка на компанию
        description: Описание компании
        area: Регион расположения
        open_vacancies: Количество открытых вакансий
    """

    def __init__(
        self,
        employer_id: int,
        name: str,
        url: Optional[str] = None,
        description: Optional[str] = None,
        area: Optional[str] = None,
        open_vacancies: Optional[int] = None,
    ) -> None:
        """
        Инициализирует экземпляр класса Company.

        Args:
            employer_id: Идентификатор работодателя из hh.ru
            name: Название компании
            url: Ссылка на компанию
            description: Описание компании
            area: Регион расположения
            open_vacancies: Количество открытых вакансий
        """
        self.employer_id = employer_id
        self.name = name
        self.url = url
        self.description = description
        self.area = area
        self.open_vacancies = open_vacancies

    @classmethod
    def from_api_data(cls, data: Dict[str, Any]) -> "Company":
        """
        Создает объект Company из данных API hh.ru.

        Args:
            data: Словарь с данными работодателя из API hh.ru

        Returns:
            Объект Company

        Example:
            >>> api_data = {"id": "1455", "name": "HeadHunter", ...}
            >>> company = Company.from_api_data(api_data)
            >>> print(company.name)
            HeadHunter
        """
        employer_id = int(data.get("id", 0))
        name = data.get("name", "")
        url = data.get("alternate_url") or data.get("url")
        description = data.get("description")
        open_vacancies = data.get("open_vacancies")

        # Извлекаем регион из объекта area, если он есть
        area_obj = data.get("area")
        area = None
        if isinstance(area_obj, dict):
            area = area_obj.get("name")
        elif isinstance(area_obj, str):
            area = area_obj

        return cls(
            employer_id=employer_id,
            name=name,
            url=url,
            description=description,
            area=area,
            open_vacancies=open_vacancies,
        )

    def to_db_tuple(self) -> Tuple[int, str, Optional[str], Optional[str], Optional[str], Optional[int]]:
        """
        Преобразует объект Company в кортеж для вставки в базу данных.

        Returns:
            Кортеж с данными в порядке полей таблицы employers:
            (employer_id, name, url, description, area, open_vacancies)

        Example:
            >>> company = Company(1455, "HeadHunter", "https://hh.ru/employer/1455")
            >>> data = company.to_db_tuple()
            >>> print(data)
            (1455, 'HeadHunter', 'https://hh.ru/employer/1455', None, None, None)
        """
        return (
            self.employer_id,
            self.name,
            self.url,
            self.description,
            self.area,
            self.open_vacancies,
        )

    def __repr__(self) -> str:
        """
        Возвращает строковое представление объекта Company.

        Returns:
            Строковое представление объекта
        """
        return (
            f"Company(employer_id={self.employer_id}, "
            f"name='{self.name}', "
            f"url='{self.url}', "
            f"area='{self.area}', "
            f"open_vacancies={self.open_vacancies})"
        )
