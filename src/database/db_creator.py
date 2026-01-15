"""Модуль для создания базы данных и таблиц.

Модуль содержит класс DBCreator для автоматического создания
базы данных PostgreSQL и таблиц для хранения данных о работодателях и вакансиях.
"""

# 1. Импорты стандартной библиотеки
import logging
import os
from pathlib import Path
from typing import Optional, cast

# 2. Импорты сторонних библиотек
import psycopg2
from dotenv import load_dotenv
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

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

    log_file = logs_dir / "db_creator.log"
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
class DBCreator:
    """Класс для создания базы данных и таблиц PostgreSQL.

    Предоставляет методы для автоматического создания БД,
    таблиц и управления структурой базы данных.
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
        Инициализирует экземпляр класса DBCreator.

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

    def _get_connection_to_postgres(self) -> psycopg2.extensions.connection:
        """
        Создает подключение к серверу PostgreSQL (к базе данных postgres).

        Используется для создания новой базы данных, так как нельзя
        создать БД, подключившись к несуществующей БД.

        Returns:
            Подключение к PostgreSQL

        Raises:
            psycopg2.Error: При ошибке подключения
        """
        try:
            conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database="postgres",  # Подключаемся к стандартной БД
                user=self.user,
                password=self.password,
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            logger.info("Подключение к серверу PostgreSQL установлено")
            return conn
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к PostgreSQL: {e}")
            raise

    def _get_connection_to_database(self) -> psycopg2.extensions.connection:
        """
        Создает подключение к целевой базе данных.

        Returns:
            Подключение к базе данных

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
            logger.info(f"Подключение к базе данных {self.database} установлено")
            return conn
        except psycopg2.Error as e:
            logger.error(f"Ошибка подключения к базе данных {self.database}: {e}")
            raise

    def create_database(self) -> None:
        """
        Создает базу данных, если она не существует.

        Raises:
            psycopg2.Error: При ошибке создания базы данных
        """
        logger.info(f"Начало создания базы данных {self.database}")

        try:
            conn = self._get_connection_to_postgres()
            cursor = conn.cursor()

            # Проверяем, существует ли база данных
            cursor.execute(
                """
                SELECT 1 FROM pg_database WHERE datname = %s
                """,
                (self.database,),
            )

            if cursor.fetchone():
                logger.info(f"База данных {self.database} уже существует")
            else:
                # Создаем базу данных
                cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.database)))
                logger.info(f"База данных {self.database} успешно создана")

            cursor.close()
            conn.close()

        except psycopg2.Error as e:
            logger.error(f"Ошибка при создании базы данных: {e}")
            raise

    def create_tables(self) -> None:
        """
        Создает таблицы в базе данных, если они не существуют.

        Создает следующие таблицы:
        - employers: таблица работодателей
        - vacancies: таблица вакансий

        Raises:
            psycopg2.Error: При ошибке создания таблиц
        """
        logger.info("Начало создания таблиц")

        try:
            conn = self._get_connection_to_database()
            cursor = conn.cursor()

            # Создание таблицы employers
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS employers (
                    employer_id INTEGER PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    url VARCHAR(500),
                    description TEXT,
                    area VARCHAR(100),
                    open_vacancies INTEGER
                )
                """
            )
            logger.info("Таблица employers создана или уже существует")

            # Создание индекса для employers
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_employers_name
                ON employers(name)
                """
            )

            # Создание таблицы vacancies
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    vacancy_id INTEGER PRIMARY KEY,
                    employer_id INTEGER NOT NULL,
                    name VARCHAR(500) NOT NULL,
                    url VARCHAR(500),
                    salary_from INTEGER,
                    salary_to INTEGER,
                    currency VARCHAR(10),
                    requirement TEXT,
                    responsibility TEXT,
                    published_at TIMESTAMP,
                    CONSTRAINT fk_employer
                        FOREIGN KEY (employer_id)
                        REFERENCES employers(employer_id)
                        ON DELETE CASCADE
                )
                """
            )
            logger.info("Таблица vacancies создана или уже существует")

            # Создание индексов для vacancies
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_vacancies_employer_id
                ON vacancies(employer_id)
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_vacancies_salary_from
                ON vacancies(salary_from)
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_vacancies_name
                ON vacancies(name)
                """
            )

            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_vacancies_published_at
                ON vacancies(published_at)
                """
            )

            conn.commit()
            logger.info("Все таблицы и индексы успешно созданы")

            cursor.close()
            conn.close()

        except psycopg2.Error as e:
            logger.error(f"Ошибка при создании таблиц: {e}")
            if conn:
                conn.rollback()
            raise

    def drop_tables(self) -> None:
        """
        Удаляет все таблицы из базы данных.

        ВНИМАНИЕ: Это удалит все данные в таблицах!

        Raises:
            psycopg2.Error: При ошибке удаления таблиц
        """
        logger.warning("Начало удаления таблиц")

        try:
            conn = self._get_connection_to_database()
            cursor = conn.cursor()

            # Удаление таблицы vacancies (сначала, так как она зависит от employers)
            cursor.execute("DROP TABLE IF EXISTS vacancies CASCADE")
            logger.info("Таблица vacancies удалена")

            # Удаление таблицы employers
            cursor.execute("DROP TABLE IF EXISTS employers CASCADE")
            logger.info("Таблица employers удалена")

            conn.commit()
            logger.info("Все таблицы успешно удалены")

            cursor.close()
            conn.close()

        except psycopg2.Error as e:
            logger.error(f"Ошибка при удалении таблиц: {e}")
            if conn:
                conn.rollback()
            raise

    def database_exists(self) -> bool:
        """
        Проверяет, существует ли база данных.

        Returns:
            True, если база данных существует, False в противном случае
        """
        try:
            conn = self._get_connection_to_postgres()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 1 FROM pg_database WHERE datname = %s
                """,
                (self.database,),
            )

            exists = cursor.fetchone() is not None

            cursor.close()
            conn.close()

            return exists

        except psycopg2.Error as e:
            logger.error(f"Ошибка при проверке существования базы данных: {e}")
            return False

    def tables_exist(self) -> bool:
        """
        Проверяет, существуют ли таблицы в базе данных.

        Returns:
            True, если обе таблицы существуют, False в противном случае
        """
        try:
            conn = self._get_connection_to_database()
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('employers', 'vacancies')
                """
            )

            result = cursor.fetchone()
            count = cast(int, result[0]) if result else 0
            exists = count == 2

            cursor.close()
            conn.close()

            return exists

        except psycopg2.Error as e:
            logger.error(f"Ошибка при проверке существования таблиц: {e}")
            return False
