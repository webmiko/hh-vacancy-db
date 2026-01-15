"""Модуль для загрузки данных из API hh.ru в базу данных.

Модуль содержит функции для получения данных о работодателях и вакансиях
через API и загрузки их в PostgreSQL.
"""

# 1. Импорты стандартной библиотеки
import logging
from pathlib import Path
from typing import List, Optional

# 2. Импорты сторонних библиотек
import psycopg2
from psycopg2.extras import execute_values

# 3. Импорты из проекта
from src.api.hh_api import HeadHunterAPI
from src.models.company import Company
from src.models.vacancy import Vacancy

# 4. Константы модуля
ENCODING = "utf-8"

# Список ID компаний для загрузки (минимум 10)
DEFAULT_EMPLOYER_IDS = [
    1455,   # HeadHunter
    3529,   # Сбер
    78638,  # Тинькофф
    1122462,  # Яндекс
    1740,   # МТС
    15478,  # VK
    2180,   # Озон
    87021,  # Альфа-Банк
    907345,  # Мегафон
    4934,   # Ростелеком
]


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

    log_file = logs_dir / "data_loader.log"
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


# 7. Публичные функции
def load_data_to_db(
    employer_ids: Optional[List[int]] = None,
    host: Optional[str] = None,
    port: Optional[int] = None,
    database: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
) -> None:
    """
    Загружает данные о работодателях и вакансиях из API hh.ru в базу данных.

    Получает данные о компаниях и их вакансиях через API hh.ru,
    создает объекты Company и Vacancy, и вставляет их в БД.

    Args:
        employer_ids: Список ID работодателей для загрузки.
                     Если не указан, используется DEFAULT_EMPLOYER_IDS
        host: Хост базы данных
        port: Порт базы данных
        database: Имя базы данных
        user: Имя пользователя
        password: Пароль

    Example:
        >>> load_data_to_db([1455, 3529])
        Загрузка данных о 2 компаниях...
    """
    import os
    from dotenv import load_dotenv

    load_dotenv()

    if employer_ids is None:
        employer_ids = DEFAULT_EMPLOYER_IDS

    logger.info(f"Начало загрузки данных о {len(employer_ids)} компаниях")

    # Инициализация API
    api = HeadHunterAPI()

    # Параметры подключения к БД
    db_host = host or os.getenv("DB_HOST", "localhost")
    db_port = port or int(os.getenv("DB_PORT", "5432"))
    db_name = database or os.getenv("DB_NAME", "hh_vacancies")
    db_user = user or os.getenv("DB_USER", "postgres")
    db_password = password or os.getenv("DB_PASSWORD", "")

    # Подключение к БД
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password,
        )
        cursor = conn.cursor()
        logger.info(f"Подключение к базе данных {db_name} установлено")
    except psycopg2.Error as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        raise

    companies_loaded = 0
    vacancies_loaded = 0

    try:
        for employer_id in employer_ids:
            logger.info(f"Обработка работодателя с ID: {employer_id}")

            # Получаем данные о работодателе и вакансиях
            data = api.get_employer_vacancies(employer_id)

            if not data["employer"]:
                logger.warning(f"Не удалось получить данные о работодателе {employer_id}")
                continue

            # Создаем объект Company
            try:
                company = Company.from_api_data(data["employer"])
            except (ValueError, KeyError, TypeError) as e:
                logger.error(f"Ошибка создания объекта Company для {employer_id}: {e}")
                continue

            # Вставляем компанию в БД (ON CONFLICT DO NOTHING для избежания дубликатов)
            try:
                insert_company_query = """
                    INSERT INTO employers (employer_id, name, url, description, area, open_vacancies)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (employer_id) DO UPDATE
                    SET name = EXCLUDED.name,
                        url = EXCLUDED.url,
                        description = EXCLUDED.description,
                        area = EXCLUDED.area,
                        open_vacancies = EXCLUDED.open_vacancies
                """
                cursor.execute(insert_company_query, company.to_db_tuple())
                companies_loaded += 1
                logger.info(f"Компания '{company.name}' загружена в БД")
            except psycopg2.Error as e:
                logger.error(f"Ошибка вставки компании {employer_id}: {e}")
                conn.rollback()
                continue

            # Обрабатываем вакансии
            vacancies_data = data["vacancies"]
            if not vacancies_data:
                logger.info(f"У работодателя {employer_id} нет вакансий")
                continue

            vacancies_to_insert = []
            for vacancy_data in vacancies_data:
                try:
                    vacancy = Vacancy.from_api_data(vacancy_data, employer_id=employer_id)
                    vacancies_to_insert.append(vacancy.to_db_tuple())
                except (ValueError, KeyError, TypeError) as e:
                    logger.warning(f"Ошибка создания объекта Vacancy: {e}")
                    continue

            # Массовая вставка вакансий (ON CONFLICT DO NOTHING)
            if vacancies_to_insert:
                try:
                    insert_vacancy_query = """
                        INSERT INTO vacancies 
                        (vacancy_id, employer_id, name, url, salary_from, salary_to, 
                         currency, requirement, responsibility, published_at)
                        VALUES %s
                        ON CONFLICT (vacancy_id) DO UPDATE
                        SET employer_id = EXCLUDED.employer_id,
                            name = EXCLUDED.name,
                            url = EXCLUDED.url,
                            salary_from = EXCLUDED.salary_from,
                            salary_to = EXCLUDED.salary_to,
                            currency = EXCLUDED.currency,
                            requirement = EXCLUDED.requirement,
                            responsibility = EXCLUDED.responsibility,
                            published_at = EXCLUDED.published_at
                    """
                    execute_values(cursor, insert_vacancy_query, vacancies_to_insert)
                    vacancies_loaded += len(vacancies_to_insert)
                    logger.info(f"Загружено {len(vacancies_to_insert)} вакансий для компании '{company.name}'")
                except psycopg2.Error as e:
                    logger.error(f"Ошибка вставки вакансий для {employer_id}: {e}")
                    conn.rollback()
                    continue

            # Коммитим после каждой компании
            conn.commit()

        logger.info(f"Загрузка завершена. Компаний: {companies_loaded}, Вакансий: {vacancies_loaded}")

    except Exception as e:
        logger.critical(f"Критическая ошибка при загрузке данных: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
        logger.info("Подключение к базе данных закрыто")
