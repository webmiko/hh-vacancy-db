"""Модуль для работы с базой данных PostgreSQL.

Модуль содержит класс DBManager для выполнения запросов к БД
и получения данных о работодателях и вакансиях.
"""

# 1. Импорты стандартной библиотеки
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

# 2. Импорты сторонних библиотек
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

# 3. Импорты из проекта
# (нет локальных импортов)

# 4. Константы модуля
ENCODING = "utf-8"

# Загрузка переменных окружения
load_dotenv()


# 5. Приватные функции
def _setup_logger() -> logging.Logger:
    """
    Настраивает и возвращает логгер для модуля.

    Returns:
        Настроенный логгер для модуля
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    logs_dir = Path(__file__).parent.parent.parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "db_manager.log"
    file_handler = logging.FileHandler(log_file, mode="w", encoding=ENCODING)
    file_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


# 6. Создаем логгер для модуля
logger = _setup_logger()


# 7. Публичные классы
class DBManager:
    """Класс для работы с базой данных PostgreSQL.

    Предоставляет методы для получения данных о работодателях и вакансиях
    из базы данных PostgreSQL.

    Attributes:
        host: Хост базы данных
        port: Порт базы данных
        database: Имя базы данных
        user: Имя пользователя
        password: Пароль
    """

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        database: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
    ) -> None:
        """
        Инициализирует экземпляр класса DBManager.

        Args:
            host: Хост базы данных (по умолчанию из переменной окружения DB_HOST)
            port: Порт базы данных (по умолчанию из переменной окружения DB_PORT или 5432)
            database: Имя базы данных (по умолчанию из переменной окружения DB_NAME)
            user: Имя пользователя (по умолчанию из переменной окружения DB_USER)
            password: Пароль (по умолчанию из переменной окружения DB_PASSWORD)
        """
        self.host = host or os.getenv("DB_HOST", "localhost")
        self.port = port or int(os.getenv("DB_PORT", "5432"))
        self.database = database or os.getenv("DB_NAME", "hh_vacancies")
        self.user = user or os.getenv("DB_USER", "postgres")
        self.password = password or os.getenv("DB_PASSWORD", "")

    def _get_connection(self) -> psycopg2.extensions.connection:
        """
        Создает подключение к базе данных.

        Returns:
            Подключение к PostgreSQL

        Raises:
            psycopg2.Error: При ошибке подключения
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
            )
            return conn
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise

    def get_companies_and_vacancies_count(self) -> List[Dict[str, Any]]:
        """
        Получает список всех компаний и количество вакансий у каждой компании.

        Использует SQL запрос с JOIN для объединения таблиц employers и vacancies.

        Returns:
            Список словарей с ключами:
            - 'name': название компании
            - 'vacancies_count': количество вакансий

        Example:
            >>> db = DBManager()
            >>> result = db.get_companies_and_vacancies_count()
            >>> print(result[0]['name'])
            HeadHunter
            >>> print(result[0]['vacancies_count'])
            42
        """
        logger.info("Получение списка компаний и количества вакансий")

        query = """
            SELECT
                e.name,
                COUNT(v.vacancy_id) as vacancies_count
            FROM employers e
            LEFT JOIN vacancies v ON e.employer_id = v.employer_id
            GROUP BY e.employer_id, e.name
            ORDER BY vacancies_count DESC, e.name
        """

        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            # Преобразуем результаты в список словарей
            result_list = [dict(row) for row in results]
            logger.info(f"Получено {len(result_list)} компаний")
            return result_list

        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise

    def get_all_vacancies(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии, зарплаты и ссылки на вакансию.

        Использует SQL запрос с JOIN для объединения таблиц employers и vacancies.

        Returns:
            Список словарей с ключами:
            - 'company_name': название компании
            - 'vacancy_name': название вакансии
            - 'salary_from': зарплата от
            - 'salary_to': зарплата до
            - 'currency': валюта
            - 'url': ссылка на вакансию

        Example:
            >>> db = DBManager()
            >>> result = db.get_all_vacancies()
            >>> print(result[0]['company_name'])
            HeadHunter
            >>> print(result[0]['vacancy_name'])
            Python Developer
        """
        logger.info("Получение списка всех вакансий")

        query = """
            SELECT
                e.name as company_name,
                v.name as vacancy_name,
                v.salary_from,
                v.salary_to,
                v.currency,
                v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            ORDER BY v.salary_from DESC NULLS LAST, v.name
        """

        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            # Преобразуем результаты в список словарей
            result_list = [dict(row) for row in results]
            logger.info(f"Получено {len(result_list)} вакансий")
            return result_list

        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям.

        Использует SQL функцию AVG для вычисления средней зарплаты.
        Учитываются только вакансии с указанной зарплатой (salary_from IS NOT NULL).

        Returns:
            Средняя зарплата (float). Возвращает 0.0, если нет вакансий с зарплатой.

        Example:
            >>> db = DBManager()
            >>> avg = db.get_avg_salary()
            >>> print(f"Средняя зарплата: {avg:.2f}")
            Средняя зарплата: 150000.00
        """
        logger.info("Получение средней зарплаты")

        query = """
            SELECT AVG(salary_from) as avg_salary
            FROM vacancies
            WHERE salary_from IS NOT NULL
        """

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute(query)
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            avg_salary = result[0] if result and result[0] is not None else 0.0
            logger.info(f"Средняя зарплата: {avg_salary:.2f}")
            return float(avg_salary)

        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise

    def get_vacancies_with_higher_salary(self) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.

        Использует SQL запрос с подзапросом для вычисления средней зарплаты
        и фильтрацию WHERE для отбора вакансий.

        Returns:
            Список словарей с данными о вакансиях (все поля таблицы vacancies).

        Example:
            >>> db = DBManager()
            >>> result = db.get_vacancies_with_higher_salary()
            >>> print(len(result))
            15
        """
        logger.info("Получение вакансий с зарплатой выше средней")

        query = """
            SELECT *
            FROM vacancies
            WHERE salary_from > (
                SELECT AVG(salary_from)
                FROM vacancies
                WHERE salary_from IS NOT NULL
            )
            ORDER BY salary_from DESC
        """

        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            # Преобразуем результаты в список словарей
            result_list = [dict(row) for row in results]
            logger.info(f"Найдено {len(result_list)} вакансий с зарплатой выше средней")
            return result_list

        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise

    def get_vacancies_with_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий, в названии которых содержатся
        переданные в метод слова.

        Использует SQL оператор LIKE для поиска по ключевым словам.

        Args:
            keyword: Ключевое слово для поиска (например, "python")

        Returns:
            Список словарей с данными о вакансиях (все поля таблицы vacancies).

        Example:
            >>> db = DBManager()
            >>> result = db.get_vacancies_with_keyword("python")
            >>> print(len(result))
            25
        """
        logger.info(f"Поиск вакансий по ключевому слову: {keyword}")

        if not keyword or not keyword.strip():
            logger.warning("Передано пустое ключевое слово")
            return []

        # Используем параметризованный запрос для защиты от SQL-инъекций
        query = """
            SELECT *
            FROM vacancies
            WHERE LOWER(name) LIKE LOWER(%s)
            ORDER BY salary_from DESC NULLS LAST, name
        """

        # Формируем паттерн для поиска (содержит ключевое слово)
        search_pattern = f"%{keyword.strip()}%"

        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query, (search_pattern,))
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            # Преобразуем результаты в список словарей
            result_list = [dict(row) for row in results]
            logger.info(f"Найдено {len(result_list)} вакансий по ключевому слову '{keyword}'")
            return result_list

        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise

    def get_vacancies_by_company(self, company_name: str) -> List[Dict[str, Any]]:
        """
        Получает список всех вакансий указанной компании.

        Использует SQL запрос с JOIN для объединения таблиц employers и vacancies
        и фильтрацию по названию компании.

        Args:
            company_name: Название компании для поиска (например, "HeadHunter")

        Returns:
            Список словарей с данными о вакансиях. Каждый словарь содержит:
            - Все поля таблицы vacancies
            - 'company_name': название компании

        Example:
            >>> db = DBManager()
            >>> result = db.get_vacancies_by_company("HeadHunter")
            >>> print(len(result))
            42
            >>> print(result[0]['company_name'])
            HeadHunter
        """
        logger.info(f"Поиск вакансий по компании: {company_name}")

        if not company_name or not company_name.strip():
            logger.warning("Передано пустое название компании")
            return []

        # Используем параметризованный запрос для защиты от SQL-инъекций
        query = """
            SELECT
                v.*,
                e.name as company_name
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.employer_id
            WHERE LOWER(e.name) LIKE LOWER(%s)
            ORDER BY v.salary_from DESC NULLS LAST, v.name
        """

        # Формируем паттерн для поиска (содержит название компании)
        search_pattern = f"%{company_name.strip()}%"

        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query, (search_pattern,))
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            # Преобразуем результаты в список словарей
            result_list = [dict(row) for row in results]
            logger.info(f"Найдено {len(result_list)} вакансий для компании '{company_name}'")
            return result_list

        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise

    def get_companies_list(self) -> List[Dict[str, Any]]:
        """
        Получает список всех компаний из базы данных.

        Returns:
            Список словарей с данными о компаниях. Каждый словарь содержит:
            - 'employer_id': идентификатор компании
            - 'name': название компании
            - 'url': ссылка на компанию
            - 'area': регион

        Example:
            >>> db = DBManager()
            >>> result = db.get_companies_list()
            >>> print(result[0]['name'])
            HeadHunter
        """
        logger.info("Получение списка всех компаний")

        query = """
            SELECT
                employer_id,
                name,
                url,
                area
            FROM employers
            ORDER BY name
        """

        try:
            conn = self._get_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)

            cursor.execute(query)
            results = cursor.fetchall()

            cursor.close()
            conn.close()

            # Преобразуем результаты в список словарей
            result_list = [dict(row) for row in results]
            logger.info(f"Получено {len(result_list)} компаний")
            return result_list

        except psycopg2.Error as e:
            logger.error(f"Ошибка при выполнении запроса: {e}")
            raise
