# Проектирование базы данных

## Анализ данных из API hh.ru

### Структура данных работодателя (employer)

Из API hh.ru работодатель содержит следующие поля:
- `id` (integer) - уникальный идентификатор работодателя
- `name` (string) - название компании
- `url` (string) - ссылка на страницу компании
- `alternate_url` (string) - альтернативная ссылка
- `open_vacancies` (integer) - количество открытых вакансий
- `description` (string, nullable) - описание компании
- `area` (object) - регион (содержит id, name)
- `industries` (array) - отрасли деятельности
- `site_url` (string, nullable) - сайт компании
- `vacancies_url` (string) - ссылка на вакансии компании

### Структура данных вакансии (vacancy)

Из API hh.ru вакансия содержит следующие поля:
- `id` (integer) - уникальный идентификатор вакансии
- `name` (string) - название вакансии
- `alternate_url` (string) - ссылка на вакансию на hh.ru
- `url` (string) - ссылка на API вакансии
- `salary` (object, nullable) - зарплата:
  - `from` (integer, nullable) - зарплата от
  - `to` (integer, nullable) - зарплата до
  - `currency` (string) - валюта (RUR, USD, EUR и т.д.)
  - `gross` (boolean) - указана ли зарплата до вычета налогов
- `snippet` (object) - краткое описание:
  - `requirement` (string, nullable) - требования
  - `responsibility` (string, nullable) - обязанности
- `description` (string, nullable) - полное описание вакансии
- `employer` (object) - работодатель:
  - `id` (integer) - ID работодателя
  - `name` (string) - название компании
  - `url` (string) - ссылка на компанию
- `published_at` (string) - дата публикации (ISO 8601)
- `created_at` (string) - дата создания (ISO 8601)

## Концептуальная модель (ER-диаграмма)

### Сущности

1. **Employers (Работодатели)**
   - Хранит информацию о компаниях
   - Первичный ключ: `employer_id`

2. **Vacancies (Вакансии)**
   - Хранит информацию о вакансиях
   - Первичный ключ: `vacancy_id`
   - Внешний ключ: `employer_id` → `employers.employer_id`

### Связи

- **Один ко многим**: Один работодатель может иметь много вакансий
- Связь реализуется через внешний ключ `employer_id` в таблице `vacancies`

## Логическая модель (Таблицы)

### Таблица: employers

| Поле | Тип данных | Ограничения | Описание |
|------|------------|-------------|----------|
| employer_id | INTEGER | PRIMARY KEY, NOT NULL | ID работодателя из hh.ru |
| name | VARCHAR(255) | NOT NULL | Название компании |
| url | VARCHAR(500) | NULL | Ссылка на компанию |
| description | TEXT | NULL | Описание компании |
| area | VARCHAR(100) | NULL | Регион |
| open_vacancies | INTEGER | NULL | Количество открытых вакансий |

**Индексы:**
- PRIMARY KEY на `employer_id`
- INDEX на `name` (для поиска)

### Таблица: vacancies

| Поле | Тип данных | Ограничения | Описание |
|------|------------|-------------|----------|
| vacancy_id | INTEGER | PRIMARY KEY, NOT NULL | ID вакансии из hh.ru |
| employer_id | INTEGER | FOREIGN KEY, NOT NULL | ID работодателя |
| name | VARCHAR(500) | NOT NULL | Название вакансии |
| url | VARCHAR(500) | NULL | Ссылка на вакансию |
| salary_from | INTEGER | NULL | Зарплата от |
| salary_to | INTEGER | NULL | Зарплата до |
| currency | VARCHAR(10) | NULL | Валюта (RUR, USD, EUR) |
| requirement | TEXT | NULL | Требования |
| responsibility | TEXT | NULL | Обязанности |
| published_at | TIMESTAMP | NULL | Дата публикации |

**Индексы:**
- PRIMARY KEY на `vacancy_id`
- FOREIGN KEY на `employer_id` → `employers.employer_id`
- INDEX на `employer_id` (для JOIN запросов)
- INDEX на `salary_from` (для фильтрации по зарплате)
- INDEX на `name` (для поиска по ключевым словам)

## Физическая модель (SQL)

### Создание таблицы employers

```sql
CREATE TABLE IF NOT EXISTS employers (
    employer_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500),
    description TEXT,
    area VARCHAR(100),
    open_vacancies INTEGER
);

CREATE INDEX IF NOT EXISTS idx_employers_name ON employers(name);
```

### Создание таблицы vacancies

```sql
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
);

CREATE INDEX IF NOT EXISTS idx_vacancies_employer_id ON vacancies(employer_id);
CREATE INDEX IF NOT EXISTS idx_vacancies_salary_from ON vacancies(salary_from);
CREATE INDEX IF NOT EXISTS idx_vacancies_name ON vacancies(name);
```

## Ограничения и правила

### Первичные ключи
- `employers.employer_id` - уникальный идентификатор работодателя
- `vacancies.vacancy_id` - уникальный идентификатор вакансии

### Внешние ключи
- `vacancies.employer_id` → `employers.employer_id`
  - ON DELETE CASCADE - при удалении работодателя удаляются все его вакансии
  - NOT NULL - вакансия всегда должна быть привязана к работодателю

### Логические ограничения
- `employers.name` - NOT NULL (обязательное поле)
- `vacancies.name` - NOT NULL (обязательное поле)
- `vacancies.employer_id` - NOT NULL (обязательное поле)
- `vacancies.salary_from` и `vacancies.salary_to` - могут быть NULL (не все вакансии имеют зарплату)
- `vacancies.currency` - может быть NULL (если зарплата не указана)

## Нормализация

База данных соответствует **3-й нормальной форме (3НФ)**:

1. **1НФ**: Все поля атомарны (не содержат множественных значений)
2. **2НФ**: Нет частичных зависимостей (все неключевые поля зависят от полного первичного ключа)
3. **3НФ**: Нет транзитивных зависимостей (неключевые поля не зависят друг от друга)

## Оптимизация

### Индексы для производительности

1. **idx_employers_name** - для поиска компаний по названию
2. **idx_vacancies_employer_id** - для JOIN запросов между таблицами
3. **idx_vacancies_salary_from** - для фильтрации и сортировки по зарплате
4. **idx_vacancies_name** - для поиска вакансий по ключевым словам (LIKE запросы)

### Рекомендации

- Использовать параметризованные запросы для защиты от SQL-инъекций
- Регулярно обновлять статистику индексов (ANALYZE)
- Рассмотреть партиционирование таблицы vacancies по дате, если данных будет много
