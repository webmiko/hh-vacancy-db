-- Создание таблиц для проекта hh-vacancy-db
-- Использование: psql -U postgres -d hh_vacancies -f create_tables.sql

-- Создание таблицы работодателей
CREATE TABLE IF NOT EXISTS employers (
    employer_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(500),
    description TEXT,
    area VARCHAR(100),
    open_vacancies INTEGER
);

-- Комментарии к таблице и полям
COMMENT ON TABLE employers IS 'Таблица работодателей (компаний) с hh.ru';
COMMENT ON COLUMN employers.employer_id IS 'Уникальный идентификатор работодателя из hh.ru';
COMMENT ON COLUMN employers.name IS 'Название компании';
COMMENT ON COLUMN employers.url IS 'Ссылка на страницу компании на hh.ru';
COMMENT ON COLUMN employers.description IS 'Описание компании';
COMMENT ON COLUMN employers.area IS 'Регион расположения компании';
COMMENT ON COLUMN employers.open_vacancies IS 'Количество открытых вакансий';

-- Создание индекса для поиска по названию компании
CREATE INDEX IF NOT EXISTS idx_employers_name ON employers(name);

-- Создание таблицы вакансий
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

-- Комментарии к таблице и полям
COMMENT ON TABLE vacancies IS 'Таблица вакансий с hh.ru';
COMMENT ON COLUMN vacancies.vacancy_id IS 'Уникальный идентификатор вакансии из hh.ru';
COMMENT ON COLUMN vacancies.employer_id IS 'Идентификатор работодателя (внешний ключ)';
COMMENT ON COLUMN vacancies.name IS 'Название вакансии';
COMMENT ON COLUMN vacancies.url IS 'Ссылка на вакансию на hh.ru';
COMMENT ON COLUMN vacancies.salary_from IS 'Зарплата от (в указанной валюте)';
COMMENT ON COLUMN vacancies.salary_to IS 'Зарплата до (в указанной валюте)';
COMMENT ON COLUMN vacancies.currency IS 'Валюта зарплаты (RUR, USD, EUR и т.д.)';
COMMENT ON COLUMN vacancies.requirement IS 'Требования к кандидату';
COMMENT ON COLUMN vacancies.responsibility IS 'Обязанности';
COMMENT ON COLUMN vacancies.published_at IS 'Дата публикации вакансии';

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_vacancies_employer_id ON vacancies(employer_id);
CREATE INDEX IF NOT EXISTS idx_vacancies_salary_from ON vacancies(salary_from);
CREATE INDEX IF NOT EXISTS idx_vacancies_name ON vacancies(name);

-- Создание индекса для поиска по дате публикации (опционально)
CREATE INDEX IF NOT EXISTS idx_vacancies_published_at ON vacancies(published_at);
