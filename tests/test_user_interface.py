"""Тесты для модуля user_interface."""

# 1. Импорты стандартной библиотеки
from unittest.mock import Mock, patch

# 2. Импорты сторонних библиотек
import pytest

# 3. Импорты из проекта
from src.utils.user_interface import format_salary, interact_with_user

# 4. Константы модуля
# (нет констант)


# 5. Тесты для format_salary
class TestFormatSalary:
    """Тесты для функции format_salary."""

    def test_format_salary_both_values(self) -> None:
        """Тест форматирования зарплаты с обеими значениями."""
        result = format_salary(100000, 150000, "RUR")
        assert result == "100000 - 150000 RUR"

    def test_format_salary_from_only(self) -> None:
        """Тест форматирования зарплаты только с from."""
        result = format_salary(100000, None, "RUR")
        assert result == "100000 RUR"

    def test_format_salary_to_only(self) -> None:
        """Тест форматирования зарплаты только с to."""
        result = format_salary(None, 150000, "RUR")
        assert result == "150000 RUR"

    def test_format_salary_no_values(self) -> None:
        """Тест форматирования зарплаты без значений."""
        result = format_salary(None, None, None)
        assert result == "не указана"

    def test_format_salary_no_currency(self) -> None:
        """Тест форматирования зарплаты без валюты."""
        result = format_salary(100000, 150000, None)
        assert result == "100000 - 150000"

    def test_format_salary_empty_currency(self) -> None:
        """Тест форматирования зарплаты с пустой валютой."""
        result = format_salary(100000, 150000, "")
        assert result == "100000 - 150000"


# 6. Тесты для interact_with_user
class TestInteractWithUser:
    """Тесты для функции interact_with_user."""

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_exit(self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock) -> None:
        """Тест выхода из меню."""
        mock_input.return_value = "0"
        mock_db_manager = Mock()
        mock_db_manager_class.return_value = mock_db_manager

        interact_with_user()

        mock_input.assert_called()
        mock_print.assert_called()

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_1(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 1 (список компаний)."""
        mock_db_manager = Mock()
        mock_db_manager.get_companies_and_vacancies_count.return_value = [
            {"name": "Company1", "vacancies_count": 5}
        ]
        mock_db_manager_class.return_value = mock_db_manager

        # Сначала опция 1, затем выход
        mock_input.side_effect = ["1", "0"]

        interact_with_user()

        mock_db_manager.get_companies_and_vacancies_count.assert_called_once()

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_2(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 2 (список вакансий)."""
        mock_db_manager = Mock()
        mock_db_manager.get_all_vacancies.return_value = [
            {
                "company_name": "Company1",
                "name": "Vacancy1",
                "salary_from": 100000,
                "salary_to": 150000,
                "currency": "RUR",
                "url": "https://hh.ru/vacancy/1",
            }
        ]
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["2", "0"]

        interact_with_user()

        mock_db_manager.get_all_vacancies.assert_called_once()

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_3(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 3 (средняя зарплата)."""
        mock_db_manager = Mock()
        mock_db_manager.get_avg_salary.return_value = 125000.0
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["3", "0"]

        interact_with_user()

        mock_db_manager.get_avg_salary.assert_called_once()

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_4(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 4 (вакансии с зарплатой выше средней)."""
        mock_db_manager = Mock()
        mock_db_manager.get_vacancies_with_higher_salary.return_value = [
            {
                "name": "Vacancy1",
                "company_name": "Company1",
                "salary_from": 150000,
                "salary_to": 200000,
                "currency": "RUR",
                "url": "https://hh.ru/vacancy/1",
            }
        ]
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["4", "0"]

        interact_with_user()

        mock_db_manager.get_vacancies_with_higher_salary.assert_called_once()

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_5(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 5 (поиск вакансий)."""
        mock_db_manager = Mock()
        mock_db_manager.get_vacancies_with_keyword.return_value = [
            {
                "name": "Python Developer",
                "vacancy_id": 123456,
                "employer_id": 1455,
                "salary_from": 100000,
                "salary_to": 150000,
                "currency": "RUR",
                "url": "https://hh.ru/vacancy/1",
            }
        ]
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["5", "Python", "0"]

        interact_with_user()

        mock_db_manager.get_vacancies_with_keyword.assert_called_once_with("Python")

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.print")
    def test_interact_with_user_db_error(self, mock_print: Mock, mock_db_manager_class: Mock) -> None:
        """Тест обработки ошибки подключения к БД."""
        mock_db_manager_class.side_effect = Exception("Connection failed")

        interact_with_user()

        # Должно быть сообщение об ошибке
        assert any("Ошибка подключения" in str(call) for call in mock_print.call_args_list)

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_invalid_option(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест обработки невалидной опции."""
        mock_db_manager = Mock()
        mock_db_manager_class.return_value = mock_db_manager

        # Невалидная опция, затем выход
        mock_input.side_effect = ["99", "0"]

        interact_with_user()

        # Должно быть сообщение о неверном выборе
        assert any("Неверный выбор" in str(call) for call in mock_print.call_args_list)

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_1_empty_results(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 1 с пустым результатом."""
        mock_db_manager = Mock()
        mock_db_manager.get_companies_and_vacancies_count.return_value = []
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["1", "0"]

        interact_with_user()

        mock_db_manager.get_companies_and_vacancies_count.assert_called_once()

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_2_empty_results(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 2 с пустым результатом."""
        mock_db_manager = Mock()
        mock_db_manager.get_all_vacancies.return_value = []
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["2", "0"]

        interact_with_user()

        mock_db_manager.get_all_vacancies.assert_called_once()

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_3_zero_salary(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 3 с нулевой зарплатой."""
        mock_db_manager = Mock()
        mock_db_manager.get_avg_salary.return_value = 0.0
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["3", "0"]

        interact_with_user()

        mock_db_manager.get_avg_salary.assert_called_once()

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_4_empty_results(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 4 с пустым результатом."""
        mock_db_manager = Mock()
        mock_db_manager.get_vacancies_with_higher_salary.return_value = []
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["4", "0"]

        interact_with_user()

        mock_db_manager.get_vacancies_with_higher_salary.assert_called_once()

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_5_empty_keyword(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 5 с пустым ключевым словом."""
        mock_db_manager = Mock()
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["5", "", "0"]

        interact_with_user()

        # Не должно быть вызова get_vacancies_with_keyword с пустым ключом

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_5_empty_results(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 5 с пустым результатом."""
        mock_db_manager = Mock()
        mock_db_manager.get_vacancies_with_keyword.return_value = []
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["5", "Python", "0"]

        interact_with_user()

        mock_db_manager.get_vacancies_with_keyword.assert_called_once_with("Python")

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_6(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 6 (поиск вакансий по компании)."""
        mock_db_manager = Mock()
        mock_db_manager.get_companies_list.return_value = [
            {"employer_id": 1455, "name": "HeadHunter", "url": "https://hh.ru/employer/1455", "area": "Москва"}
        ]
        mock_db_manager.get_vacancies_by_company.return_value = [
            {
                "vacancy_id": 123456,
                "employer_id": 1455,
                "name": "Python Developer",
                "salary_from": 100000,
                "salary_to": 150000,
                "currency": "RUR",
                "url": "https://hh.ru/vacancy/1",
                "company_name": "HeadHunter",
            }
        ]
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["6", "HeadHunter", "0"]

        interact_with_user()

        mock_db_manager.get_companies_list.assert_called_once()
        mock_db_manager.get_vacancies_by_company.assert_called_once_with("HeadHunter")

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_6_empty_company(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 6 с пустым названием компании."""
        mock_db_manager = Mock()
        mock_db_manager.get_companies_list.return_value = [
            {"employer_id": 1455, "name": "HeadHunter", "url": "https://hh.ru/employer/1455", "area": "Москва"}
        ]
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["6", "", "0"]

        interact_with_user()

        mock_db_manager.get_vacancies_by_company.assert_not_called()

    @patch("src.utils.user_interface.DBManager")
    @patch("builtins.input")
    @patch("builtins.print")
    def test_interact_with_user_option_6_empty_results(
        self, mock_print: Mock, mock_input: Mock, mock_db_manager_class: Mock
    ) -> None:
        """Тест выбора опции 6 с пустым результатом."""
        mock_db_manager = Mock()
        mock_db_manager.get_companies_list.return_value = [
            {"employer_id": 1455, "name": "HeadHunter", "url": "https://hh.ru/employer/1455", "area": "Москва"}
        ]
        mock_db_manager.get_vacancies_by_company.return_value = []
        mock_db_manager_class.return_value = mock_db_manager

        mock_input.side_effect = ["6", "NonExistent", "0"]

        interact_with_user()

        mock_db_manager.get_vacancies_by_company.assert_called_once_with("NonExistent")
