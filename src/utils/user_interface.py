"""Модуль пользовательского интерфейса.

Модуль содержит функцию для взаимодействия с пользователем
и отображения результатов работы с базой данных.
"""

# 1. Импорты стандартной библиотеки
from typing import Any, Dict, List

# 2. Импорты сторонних библиотек
# (нет сторонних импортов)

# 3. Импорты из проекта
from src.database.db_manager import DBManager


# 4. Константы модуля
MENU_WIDTH = 80
MAX_COMPANIES_DISPLAY = 20


# 5. Приватные функции
def _display_vacancy(vacancy: Dict[str, Any], index: int, show_company: bool = False) -> None:
    """
    Выводит информацию об одной вакансии.

    Args:
        vacancy: Словарь с данными вакансии
        index: Номер вакансии в списке
        show_company: Показывать ли название компании
    """
    name = vacancy.get("name") or vacancy.get("vacancy_name", "Неизвестно")
    salary = format_salary(
        vacancy.get("salary_from"),
        vacancy.get("salary_to"),
        vacancy.get("currency"),
    )
    url = vacancy.get("url", "не указана")

    print(f"\n{index}. {name}")
    if show_company:
        company_name = vacancy.get("company_name", "Неизвестно")
        print(f"   Компания: {company_name}")
    print(f"   Зарплата: {salary}")
    print(f"   Ссылка: {url}")


def _display_vacancies(vacancies: List[Dict[str, Any]], show_company: bool = False) -> None:
    """
    Выводит список вакансий.

    Args:
        vacancies: Список словарей с данными вакансий
        show_company: Показывать ли название компании
    """
    if not vacancies:
        return

    for i, vacancy in enumerate(vacancies, 1):
        _display_vacancy(vacancy, i, show_company)


def _handle_companies_list(db_manager: DBManager) -> None:
    """Обрабатывает запрос списка компаний и количества вакансий."""
    print("\n" + "=" * MENU_WIDTH)
    print("СПИСОК КОМПАНИЙ И КОЛИЧЕСТВО ВАКАНСИЙ")
    print("=" * MENU_WIDTH)

    results = db_manager.get_companies_and_vacancies_count()

    if not results:
        print("В базе данных нет компаний.")
    else:
        for i, company in enumerate(results, 1):
            name = company.get("name", "Неизвестно")
            count = company.get("vacancies_count", 0)
            print(f"{i}. {name}: {count} вакансий")

    print(f"\nВсего компаний: {len(results)}")


def _handle_all_vacancies(db_manager: DBManager) -> None:
    """Обрабатывает запрос списка всех вакансий."""
    print("\n" + "=" * MENU_WIDTH)
    print("СПИСОК ВСЕХ ВАКАНСИЙ")
    print("=" * MENU_WIDTH)

    results = db_manager.get_all_vacancies()

    if not results:
        print("В базе данных нет вакансий.")
    else:
        _display_vacancies(results, show_company=True)

    print(f"\nВсего вакансий: {len(results)}")


def _handle_avg_salary(db_manager: DBManager) -> None:
    """Обрабатывает запрос средней зарплаты."""
    print("\n" + "=" * MENU_WIDTH)
    print("СРЕДНЯЯ ЗАРПЛАТА ПО ВАКАНСИЯМ")
    print("=" * MENU_WIDTH)

    avg_salary = db_manager.get_avg_salary()

    if avg_salary > 0:
        print(f"\nСредняя зарплата: {avg_salary:,.0f} руб.")
    else:
        print("\nНе удалось вычислить среднюю зарплату.")
        print("Возможно, в базе данных нет вакансий с указанной зарплатой.")


def _handle_higher_salary_vacancies(db_manager: DBManager) -> None:
    """Обрабатывает запрос вакансий с зарплатой выше средней."""
    print("\n" + "=" * MENU_WIDTH)
    print("ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ")
    print("=" * MENU_WIDTH)

    results = db_manager.get_vacancies_with_higher_salary()

    if not results:
        print("В базе данных нет вакансий с зарплатой выше средней.")
    else:
        _display_vacancies(results)

    print(f"\nВсего вакансий: {len(results)}")


def _handle_keyword_search(db_manager: DBManager) -> None:
    """Обрабатывает поиск вакансий по ключевому слову."""
    keyword = input("\nВведите ключевое слово для поиска: ").strip()

    if not keyword:
        print("Ключевое слово не может быть пустым.")
        return

    print("\n" + "=" * MENU_WIDTH)
    print(f'ВАКАНСИИ ПО КЛЮЧЕВОМУ СЛОВУ "{keyword.upper()}"')
    print("=" * MENU_WIDTH)

    results = db_manager.get_vacancies_with_keyword(keyword)

    if not results:
        print(f"Вакансии по ключевому слову '{keyword}' не найдены.")
    else:
        _display_vacancies(results)

    print(f"\nНайдено вакансий: {len(results)}")


def _handle_company_search(db_manager: DBManager) -> None:
    """Обрабатывает поиск вакансий по названию компании."""
    print("\n" + "=" * MENU_WIDTH)
    print("СПИСОК КОМПАНИЙ")
    print("=" * MENU_WIDTH)

    companies = db_manager.get_companies_list()

    if not companies:
        print("В базе данных нет компаний.")
        return

    print("\nДоступные компании:")
    for i, company in enumerate(companies[:MAX_COMPANIES_DISPLAY], 1):
        name = company.get("name", "Неизвестно")
        area = company.get("area", "")
        area_str = f" ({area})" if area else ""
        print(f"  {i}. {name}{area_str}")

    if len(companies) > MAX_COMPANIES_DISPLAY:
        print(f"  ... и еще {len(companies) - MAX_COMPANIES_DISPLAY} компаний")

    company_name = input("\nВведите название компании (или часть названия): ").strip()

    if not company_name:
        print("Название компании не может быть пустым.")
        return

    print("\n" + "=" * MENU_WIDTH)
    print(f'ВАКАНСИИ КОМПАНИИ "{company_name.upper()}"')
    print("=" * MENU_WIDTH)

    results = db_manager.get_vacancies_by_company(company_name)

    if not results:
        print(f"Вакансии компании '{company_name}' не найдены.")
    else:
        # Группируем по компаниям (на случай, если найдено несколько компаний)
        companies_found: Dict[str, List[Dict[str, Any]]] = {}
        for vacancy in results:
            comp_name = vacancy.get("company_name", "Неизвестно")
            if comp_name not in companies_found:
                companies_found[comp_name] = []
            companies_found[comp_name].append(vacancy)

        for comp_name, vacancies in companies_found.items():
            print(f"\n📌 Компания: {comp_name}")
            print(f"   Найдено вакансий: {len(vacancies)}")
            print("-" * MENU_WIDTH)

            for i, vacancy in enumerate(vacancies, 1):
                _display_vacancy(vacancy, i)

    print(f"\nВсего найдено вакансий: {len(results)}")


# 6. Публичные функции
def format_salary(salary_from: Any, salary_to: Any, currency: Any) -> str:
    """
    Форматирует информацию о зарплате для вывода.

    Args:
        salary_from: Зарплата от
        salary_to: Зарплата до
        currency: Валюта

    Returns:
        Отформатированная строка с зарплатой
    """
    if salary_from is None and salary_to is None:
        return "не указана"

    parts = []
    if salary_from is not None:
        parts.append(str(salary_from))
    if salary_to is not None:
        parts.append(str(salary_to))

    salary_str = " - ".join(parts) if len(parts) > 1 else parts[0]
    currency_str = f" {currency}" if currency else ""

    return f"{salary_str}{currency_str}"


def interact_with_user() -> None:
    """
    Функция взаимодействия с пользователем.

    Предоставляет меню для работы с базой данных вакансий:
    - Получение списка компаний и количества вакансий
    - Получение списка всех вакансий
    - Получение средней зарплаты
    - Получение вакансий с зарплатой выше средней
    - Поиск вакансий по ключевому слову
    - Поиск вакансий по названию компании

    Вывод результатов в человекочитаемом формате.
    """
    print("=" * MENU_WIDTH)
    print("HH Vacancy DB - Работа с базой данных вакансий hh.ru")
    print("=" * MENU_WIDTH)

    # Инициализация DBManager
    try:
        db_manager = DBManager()
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        print("Проверьте настройки подключения в файле .env")
        return

    menu_handlers = {
        "1": _handle_companies_list,
        "2": _handle_all_vacancies,
        "3": _handle_avg_salary,
        "4": _handle_higher_salary_vacancies,
        "5": _handle_keyword_search,
        "6": _handle_company_search,
    }

    while True:
        print("\n" + "-" * MENU_WIDTH)
        print("МЕНЮ:")
        print("1. Получить список всех компаний и количество вакансий")
        print("2. Получить список всех вакансий")
        print("3. Получить среднюю зарплату по вакансиям")
        print("4. Получить вакансии с зарплатой выше средней")
        print("5. Получить вакансии по ключевому слову")
        print("6. Получить вакансии по названию компании")
        print("0. Выход")
        print("-" * MENU_WIDTH)

        choice = input("Выберите пункт меню: ").strip()

        if choice == "0":
            print("\nДо свидания!")
            break

        handler = menu_handlers.get(choice)
        if handler:
            try:
                handler(db_manager)
            except Exception as e:
                print(f"\nОшибка при получении данных: {e}")
        else:
            print("\nНеверный выбор. Пожалуйста, выберите пункт меню от 0 до 6.")
