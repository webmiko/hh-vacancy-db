#!/usr/bin/env python3
"""Скрипт для проверки подключения к базе данных PostgreSQL."""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, str(Path(__file__).parent))

try:
    import psycopg2
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("Установите зависимости: poetry install")
    sys.exit(1)

# Загружаем переменные окружения
load_dotenv()

# Получаем параметры подключения
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "hh_vacancies")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

print("=" * 80)
print("ПРОВЕРКА ПОДКЛЮЧЕНИЯ К БАЗЕ ДАННЫХ POSTGRESQL")
print("=" * 80)
print(f"\nПараметры подключения:")
print(f"  Host:     {DB_HOST}")
print(f"  Port:     {DB_PORT}")
print(f"  Database: {DB_NAME}")
print(f"  User:     {DB_USER}")
print(f"  Password: {'*' * len(DB_PASSWORD) if DB_PASSWORD else '(пустой)'}")
print()

# Проверка 1: Подключение к серверу PostgreSQL (к базе postgres)
print("1. Проверка подключения к серверу PostgreSQL...")
try:
    conn_postgres = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database="postgres",  # Подключаемся к системной БД
        user=DB_USER,
        password=DB_PASSWORD,
    )
    conn_postgres.close()
    print("   ✅ Успешно подключено к серверу PostgreSQL")
except psycopg2.OperationalError as e:
    error_msg = str(e).lower()
    if "connection refused" in error_msg:
        print("   ❌ Не удалось подключиться к серверу PostgreSQL")
        print("   ⚠️  Сервер не запущен или недоступен")
        print("\n   Рекомендации:")
        print("   • Для macOS: brew services start postgresql")
        print("   • Для Linux: sudo systemctl start postgresql")
        print("   • Для Windows: проверьте службу PostgreSQL")
        sys.exit(1)
    elif "authentication failed" in error_msg:
        print("   ❌ Ошибка аутентификации")
        print("   ⚠️  Неверное имя пользователя или пароль")
        sys.exit(1)
    else:
        print(f"   ❌ Ошибка подключения: {e}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Неожиданная ошибка: {e}")
    sys.exit(1)

# Проверка 2: Существование базы данных
print("\n2. Проверка существования базы данных...")
try:
    conn_postgres = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
    )
    cursor = conn_postgres.cursor()
    cursor.execute(
        "SELECT 1 FROM pg_database WHERE datname = %s",
        (DB_NAME,)
    )
    exists = cursor.fetchone() is not None
    cursor.close()
    conn_postgres.close()
    
    if exists:
        print(f"   ✅ База данных '{DB_NAME}' существует")
    else:
        print(f"   ⚠️  База данных '{DB_NAME}' не существует")
        print("   ℹ️  База данных будет создана автоматически при первом запуске")
except Exception as e:
    print(f"   ⚠️  Не удалось проверить существование БД: {e}")

# Проверка 3: Подключение к целевой базе данных
print(f"\n3. Проверка подключения к базе данных '{DB_NAME}'...")
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )
    cursor = conn.cursor()
    
    # Проверка версии PostgreSQL
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"   ✅ Успешно подключено к базе данных")
    print(f"   ℹ️  Версия PostgreSQL: {version.split(',')[0]}")
    
    # Проверка существования таблиц
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    if tables:
        print(f"\n   📊 Найдено таблиц: {len(tables)}")
        for table in tables:
            # Подсчет записей в таблице
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]};")
            count = cursor.fetchone()[0]
            print(f"      • {table[0]}: {count} записей")
    else:
        print("   ⚠️  Таблицы не найдены")
        print("   ℹ️  Таблицы будут созданы автоматически при первом запуске")
    
    cursor.close()
    conn.close()
    print("\n" + "=" * 80)
    print("✅ ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО")
    print("=" * 80)
    
except psycopg2.OperationalError as e:
    error_msg = str(e).lower()
    if "does not exist" in error_msg or "не существует" in error_msg:
        print(f"   ⚠️  База данных '{DB_NAME}' не существует")
        print("   ℹ️  База данных будет создана автоматически при первом запуске")
    else:
        print(f"   ❌ Ошибка подключения: {e}")
        sys.exit(1)
except Exception as e:
    print(f"   ❌ Неожиданная ошибка: {e}")
    sys.exit(1)
