-- Создание базы данных для проекта hh-vacancy-db
-- Использование: psql -U postgres -f create_database.sql

-- Создание базы данных (выполняется от имени суперпользователя)
-- Если база данных уже существует, команда завершится с ошибкой
-- Для пересоздания сначала выполните: DROP DATABASE IF EXISTS hh_vacancies;

CREATE DATABASE hh_vacancies
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Комментарий к базе данных
COMMENT ON DATABASE hh_vacancies IS 'База данных для хранения информации о работодателях и вакансиях с hh.ru';
