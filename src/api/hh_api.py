"""Класс для работы с API hh.ru.

Модуль содержит класс HeadHunterAPI для получения данных о работодателях
и вакансиях с платформы hh.ru через их публичное API.
"""

# 1. Импорты стандартной библиотеки
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

# 2. Импорты сторонних библиотек
import requests

# 3. Импорты из проекта
# (нет локальных импортов)

# 4. Константы модуля
HH_API_BASE_URL = "https://api.hh.ru"
HH_EMPLOYERS_URL = f"{HH_API_BASE_URL}/employers"
HH_VACANCIES_URL = f"{HH_API_BASE_URL}/vacancies"
HH_USER_AGENT = "HH-Vacancy-DB/1.0 (webmiko@icloud.com)"
REQUEST_TIMEOUT = 10
MAX_PAGES = 20
DEFAULT_PER_PAGE = 100
ENCODING = "utf-8"


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

    log_file = logs_dir / "hh_api.log"
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
class HeadHunterAPI:
    """Класс для работы с API hh.ru.

    Реализует методы для получения данных о работодателях и их вакансиях
    через публичное API hh.ru.

    Attributes:
        _base_url: Базовый URL API hh.ru
        _headers: Заголовки для запросов к API
    """

    def __init__(self) -> None:
        """
        Инициализирует экземпляр класса HeadHunterAPI.

        Устанавливает базовый URL и заголовки для запросов к API.
        """
        self._base_url: str = HH_API_BASE_URL
        self._headers: Dict[str, str] = {"User-Agent": HH_USER_AGENT}

    def get_employer(self, employer_id: int) -> Optional[Dict[str, Any]]:
        """
        Получает данные о работодателе по его ID.

        Args:
            employer_id: Идентификатор работодателя из hh.ru

        Returns:
            Словарь с данными о работодателе или None при ошибке

        Example:
            >>> api = HeadHunterAPI()
            >>> employer = api.get_employer(1455)
            >>> print(employer['name'])
            HeadHunter
        """
        logger.info(f"Получение данных о работодателе с ID: {employer_id}")

        if not isinstance(employer_id, int) or employer_id <= 0:
            logger.warning(f"Некорректный ID работодателя: {employer_id}")
            return None

        url = f"{HH_EMPLOYERS_URL}/{employer_id}"

        try:
            response = requests.get(url, headers=self._headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()

            employer_data = response.json()
            logger.info(f"Успешно получены данные о работодателе: {employer_data.get('name', 'Unknown')}")
            return cast(Dict[str, Any], employer_data)

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Работодатель с ID {employer_id} не найден")
            else:
                logger.error(f"HTTP ошибка при получении работодателя: {e.response.status_code} - {e}")
            return None
        except requests.RequestException as e:
            logger.error(f"Ошибка запроса к API при получении работодателя: {type(e).__name__} - {e}")
            return None
        except ValueError as e:
            logger.error(f"Ошибка парсинга JSON ответа: {type(e).__name__} - {e}")
            return None
        except Exception as e:
            logger.critical(f"Неожиданная ошибка при получении работодателя: {type(e).__name__} - {e}")
            return None

    def get_vacancies(self, employer_id: int) -> List[Dict[str, Any]]:
        """
        Получает список вакансий работодателя по его ID.

        Выполняет запросы к API hh.ru для получения всех вакансий работодателя
        с поддержкой пагинации (до MAX_PAGES страниц).

        Args:
            employer_id: Идентификатор работодателя из hh.ru

        Returns:
            Список словарей с данными о вакансиях. Возвращает пустой список при ошибке.

        Example:
            >>> api = HeadHunterAPI()
            >>> vacancies = api.get_vacancies(1455)
            >>> print(len(vacancies))
            42
        """
        logger.info(f"Получение вакансий работодателя с ID: {employer_id}")

        if not isinstance(employer_id, int) or employer_id <= 0:
            logger.warning(f"Некорректный ID работодателя: {employer_id}")
            return []

        all_vacancies: List[Dict[str, Any]] = []
        page = 0

        try:
            while page < MAX_PAGES:
                logger.debug(f"Запрос страницы {page} вакансий работодателя {employer_id}")

                params = {
                    "employer_id": employer_id,
                    "page": page,
                    "per_page": DEFAULT_PER_PAGE,
                }

                response = requests.get(
                    HH_VACANCIES_URL,
                    headers=self._headers,
                    params=params,
                    timeout=REQUEST_TIMEOUT,
                )
                response.raise_for_status()

                try:
                    response_data = response.json()
                except ValueError as e:
                    logger.error(f"Ошибка парсинга JSON ответа: {type(e).__name__} - {e}")
                    break

                if "items" not in response_data:
                    logger.warning("В ответе API отсутствует ключ 'items'")
                    break

                items = response_data["items"]
                if not isinstance(items, list):
                    logger.warning(f"Ключ 'items' не является списком. Тип: {type(items)}")
                    break

                if not items:
                    logger.info(f"Страница {page} пуста, завершение пагинации")
                    break

                all_vacancies.extend(items)
                logger.debug(f"Получено {len(items)} вакансий со страницы {page}")

                # Проверяем, есть ли еще страницы
                pages = response_data.get("pages", 0)
                if page >= pages - 1:
                    logger.debug("Достигнута последняя страница")
                    break

                page += 1

            logger.info(f"Всего получено {len(all_vacancies)} вакансий для работодателя {employer_id}")
            return all_vacancies

        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Работодатель с ID {employer_id} не найден")
            else:
                logger.error(f"HTTP ошибка при получении вакансий: {e.response.status_code} - {e}")
            return []
        except requests.RequestException as e:
            logger.error(f"Ошибка запроса к API при получении вакансий: {type(e).__name__} - {e}")
            return []
        except KeyError as e:
            logger.error(f"Ошибка: отсутствует ключ в данных API: {e}")
            return []
        except Exception as e:
            logger.critical(f"Неожиданная ошибка при получении вакансий: {type(e).__name__} - {e}")
            return []

    def get_employer_vacancies(self, employer_id: int) -> Dict[str, Any]:
        """
        Получает данные о работодателе и все его вакансии.

        Удобный метод для получения полной информации о работодателе
        и всех его вакансиях за один вызов.

        Args:
            employer_id: Идентификатор работодателя из hh.ru

        Returns:
            Словарь с ключами:
            - 'employer': данные о работодателе или None
            - 'vacancies': список вакансий или пустой список

        Example:
            >>> api = HeadHunterAPI()
            >>> data = api.get_employer_vacancies(1455)
            >>> print(data['employer']['name'])
            HeadHunter
            >>> print(len(data['vacancies']))
            42
        """
        logger.info(f"Получение полных данных о работодателе {employer_id} и его вакансиях")

        employer = self.get_employer(employer_id)
        vacancies = self.get_vacancies(employer_id) if employer else []

        return {
            "employer": employer,
            "vacancies": vacancies,
        }
