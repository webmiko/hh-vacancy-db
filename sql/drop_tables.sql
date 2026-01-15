-- Удаление таблиц для проекта hh-vacancy-db
-- Использование: psql -U postgres -d hh_vacancies -f drop_tables.sql
-- ВНИМАНИЕ: Это удалит все данные в таблицах!

-- Удаление таблицы вакансий (сначала, так как она зависит от employers)
DROP TABLE IF EXISTS vacancies CASCADE;

-- Удаление таблицы работодателей
DROP TABLE IF EXISTS employers CASCADE;

-- Примечание: CASCADE автоматически удалит все индексы и ограничения,
-- связанные с этими таблицами
