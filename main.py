"""Главный модуль программы.

Точка входа в приложение для работы с вакансиями hh.ru и базой данных PostgreSQL.
"""

# 1. Импорты стандартной библиотеки
import logging
import sys
from pathlib import Path

# 3. Импорты из проекта
from src.database.db_creator import DBCreator
from src.database.db_manager import DBManager
from src.utils.data_loader import load_data_to_db
from src.utils.user_interface import interact_with_user

# 2. Импорты сторонних библиотек
# (нет сторонних импортов)


# 4. Константы модуля
ENCODING = "utf-8"


# 5. Настройка логирования
def _setup_logging() -> None:
    """Настраивает логирование для приложения."""
    logs_dir = Path(__file__).parent / "logs"
    logs_dir.mkdir(exist_ok=True)

    log_file = logs_dir / "main.log"
    file_handler = logging.FileHandler(log_file, mode="w", encoding=ENCODING)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


# 6. Публичные функции
def main() -> None:
    """
    Главная функция приложения.

    Выполняет следующие действия:
    1. Создает базу данных (если не существует)
    2. Создает таблицы (если не существуют)
    3. Загружает данные из API hh.ru (если БД пустая)
    4. Запускает пользовательский интерфейс
    """
    _setup_logging()
    logger = logging.getLogger(__name__)

    logger.info("Запуск приложения HH Vacancy DB")

    try:
        # Создание БД и таблиц
        logger.info("Проверка и создание базы данных и таблиц...")
        db_creator = DBCreator()

        # Создаем БД, если не существует
        if not db_creator.database_exists():
            logger.info("База данных не существует. Создание...")
            db_creator.create_database()
        else:
            logger.info("База данных уже существует.")

        # Создаем таблицы, если не существуют
        if not db_creator.tables_exist():
            logger.info("Таблицы не существуют. Создание...")
            db_creator.create_tables()
        else:
            logger.info("Таблицы уже существуют.")

        # Проверяем, есть ли данные в БД
        db_manager = DBManager()
        companies = db_manager.get_companies_and_vacancies_count()

        if not companies or sum(c.get("vacancies_count", 0) for c in companies) == 0:
            logger.info("База данных пуста. Загрузка данных из API hh.ru...")
            print("\n" + "=" * 80)
            print("Загрузка данных о компаниях и вакансиях из hh.ru...")
            print("Это может занять некоторое время...")
            print("=" * 80 + "\n")

            try:
                load_data_to_db()
                print("\nДанные успешно загружены в базу данных!")
            except Exception as e:
                logger.error(f"Ошибка при загрузке данных: {e}")
                print(f"\nОшибка при загрузке данных: {e}")
                print("Продолжаем работу с существующими данными...")
        else:
            total_vacancies = sum(c.get("vacancies_count", 0) for c in companies)
            logger.info(f"В базе данных уже есть данные: {len(companies)} компаний, {total_vacancies} вакансий")
            print(f"\nВ базе данных: {len(companies)} компаний, {total_vacancies} вакансий")

        # Запуск пользовательского интерфейса
        logger.info("Запуск пользовательского интерфейса...")
        interact_with_user()

    except KeyboardInterrupt:
        logger.info("Программа прервана пользователем")
        print("\n\nПрограмма прервана пользователем. До свидания!")
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}", exc_info=True)
        print(f"\nКритическая ошибка: {e}")
        print("Проверьте логи в папке logs/ для подробной информации.")
        sys.exit(1)

    logger.info("Завершение работы приложения")


if __name__ == "__main__":
    main()
