"""Модуль пользовательского интерфейса.

Модуль содержит функцию для взаимодействия с пользователем
и отображения результатов работы с базой данных.
"""

# 1. Импорты стандартной библиотеки
from typing import Any

# 3. Импорты из проекта
from src.database.db_manager import DBManager

# 2. Импорты сторонних библиотек
# (нет сторонних импортов)


# 4. Константы модуля
# (нет констант)


# 5. Публичные функции
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

    Вывод результатов в человекочитаемом формате.
    """
    print("=" * 80)
    print("HH Vacancy DB - Работа с базой данных вакансий hh.ru")
    print("=" * 80)

    # Инициализация DBManager
    try:
        db_manager = DBManager()
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        print("Проверьте настройки подключения в файле .env")
        return

    while True:
        print("\n" + "-" * 80)
        print("МЕНЮ:")
        print("1. Получить список всех компаний и количество вакансий")
        print("2. Получить список всех вакансий")
        print("3. Получить среднюю зарплату по вакансиям")
        print("4. Получить вакансии с зарплатой выше средней")
        print("5. Получить вакансии по ключевому слову")
        print("6. Получить вакансии по названию компании")
        print("0. Выход")
        print("-" * 80)

        choice = input("Выберите пункт меню: ").strip()

        if choice == "0":
            print("\nДо свидания!")
            break

        elif choice == "1":
            try:
                print("\n" + "=" * 80)
                print("СПИСОК КОМПАНИЙ И КОЛИЧЕСТВО ВАКАНСИЙ")
                print("=" * 80)

                results = db_manager.get_companies_and_vacancies_count()

                if not results:
                    print("В базе данных нет компаний.")
                else:
                    for i, company in enumerate(results, 1):
                        name = company.get("name", "Неизвестно")
                        count = company.get("vacancies_count", 0)
                        print(f"{i}. {name}: {count} вакансий")

                print(f"\nВсего компаний: {len(results)}")

            except Exception as e:
                print(f"\nОшибка при получении данных: {e}")

        elif choice == "2":
            try:
                print("\n" + "=" * 80)
                print("СПИСОК ВСЕХ ВАКАНСИЙ")
                print("=" * 80)

                results = db_manager.get_all_vacancies()

                if not results:
                    print("В базе данных нет вакансий.")
                else:
                    for i, vacancy in enumerate(results, 1):
                        company_name = vacancy.get("company_name", "Неизвестно")
                        vacancy_name = vacancy.get("vacancy_name", "Неизвестно")
                        salary = format_salary(
                            vacancy.get("salary_from"),
                            vacancy.get("salary_to"),
                            vacancy.get("currency"),
                        )
                        url = vacancy.get("url", "не указана")

                        print(f"\n{i}. {vacancy_name}")
                        print(f"   Компания: {company_name}")
                        print(f"   Зарплата: {salary}")
                        print(f"   Ссылка: {url}")

                print(f"\nВсего вакансий: {len(results)}")

            except Exception as e:
                print(f"\nОшибка при получении данных: {e}")

        elif choice == "3":
            try:
                print("\n" + "=" * 80)
                print("СРЕДНЯЯ ЗАРПЛАТА ПО ВАКАНСИЯМ")
                print("=" * 80)

                avg_salary = db_manager.get_avg_salary()

                if avg_salary > 0:
                    print(f"\nСредняя зарплата: {avg_salary:,.0f} руб.")
                else:
                    print("\nНе удалось вычислить среднюю зарплату.")
                    print("Возможно, в базе данных нет вакансий с указанной зарплатой.")

            except Exception as e:
                print(f"\nОшибка при получении данных: {e}")

        elif choice == "4":
            try:
                print("\n" + "=" * 80)
                print("ВАКАНСИИ С ЗАРПЛАТОЙ ВЫШЕ СРЕДНЕЙ")
                print("=" * 80)

                results = db_manager.get_vacancies_with_higher_salary()

                if not results:
                    print("В базе данных нет вакансий с зарплатой выше средней.")
                else:
                    for i, vacancy in enumerate(results, 1):
                        name = vacancy.get("name", "Неизвестно")
                        salary = format_salary(
                            vacancy.get("salary_from"),
                            vacancy.get("salary_to"),
                            vacancy.get("currency"),
                        )
                        url = vacancy.get("url", "не указана")

                        print(f"\n{i}. {name}")
                        print(f"   Зарплата: {salary}")
                        print(f"   Ссылка: {url}")

                print(f"\nВсего вакансий: {len(results)}")

            except Exception as e:
                print(f"\nОшибка при получении данных: {e}")

        elif choice == "5":
            try:
                keyword = input("\nВведите ключевое слово для поиска: ").strip()

                if not keyword:
                    print("Ключевое слово не может быть пустым.")
                    continue

                print("\n" + "=" * 80)
                print(f'ВАКАНСИИ ПО КЛЮЧЕВОМУ СЛОВУ "{keyword.upper()}"')
                print("=" * 80)

                results = db_manager.get_vacancies_with_keyword(keyword)

                if not results:
                    print(f"Вакансии по ключевому слову '{keyword}' не найдены.")
                else:
                    for i, vacancy in enumerate(results, 1):
                        name = vacancy.get("name", "Неизвестно")
                        salary = format_salary(
                            vacancy.get("salary_from"),
                            vacancy.get("salary_to"),
                            vacancy.get("currency"),
                        )
                        url = vacancy.get("url", "не указана")

                        print(f"\n{i}. {name}")
                        print(f"   Зарплата: {salary}")
                        print(f"   Ссылка: {url}")

                print(f"\nНайдено вакансий: {len(results)}")

            except Exception as e:
                print(f"\nОшибка при получении данных: {e}")

        elif choice == "6":
            try:
                # Сначала показываем список компаний для удобства
                print("\n" + "=" * 80)
                print("СПИСОК КОМПАНИЙ")
                print("=" * 80)

                companies = db_manager.get_companies_list()

                if not companies:
                    print("В базе данных нет компаний.")
                    continue

                print("\nДоступные компании:")
                for i, company in enumerate(companies[:20], 1):  # Показываем первые 20
                    name = company.get("name", "Неизвестно")
                    area = company.get("area", "")
                    area_str = f" ({area})" if area else ""
                    print(f"  {i}. {name}{area_str}")

                if len(companies) > 20:
                    print(f"  ... и еще {len(companies) - 20} компаний")

                company_name = input("\nВведите название компании (или часть названия): ").strip()

                if not company_name:
                    print("Название компании не может быть пустым.")
                    continue

                print("\n" + "=" * 80)
                print(f'ВАКАНСИИ КОМПАНИИ "{company_name.upper()}"')
                print("=" * 80)

                results = db_manager.get_vacancies_by_company(company_name)

                if not results:
                    print(f"Вакансии компании '{company_name}' не найдены.")
                else:
                    # Группируем по компаниям (на случай, если найдено несколько компаний)
                    companies_found = {}
                    for vacancy in results:
                        comp_name = vacancy.get("company_name", "Неизвестно")
                        if comp_name not in companies_found:
                            companies_found[comp_name] = []
                        companies_found[comp_name].append(vacancy)

                    for comp_name, vacancies in companies_found.items():
                        print(f"\n📌 Компания: {comp_name}")
                        print(f"   Найдено вакансий: {len(vacancies)}")
                        print("-" * 80)

                        for i, vacancy in enumerate(vacancies, 1):
                            name = vacancy.get("name", "Неизвестно")
                            salary = format_salary(
                                vacancy.get("salary_from"),
                                vacancy.get("salary_to"),
                                vacancy.get("currency"),
                            )
                            url = vacancy.get("url", "не указана")

                            print(f"\n  {i}. {name}")
                            print(f"     Зарплата: {salary}")
                            print(f"     Ссылка: {url}")

                print(f"\nВсего найдено вакансий: {len(results)}")

            except Exception as e:
                print(f"\nОшибка при получении данных: {e}")

        else:
            print("\nНеверный выбор. Пожалуйста, выберите пункт меню от 0 до 6.")
