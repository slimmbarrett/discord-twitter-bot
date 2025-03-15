#!/usr/bin/env python3
"""
Скрипт для создания необходимых таблиц в базе данных Supabase
"""
import os
import sys
import requests
import json
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем учетные данные Supabase из переменных окружения
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")

def create_table(table_name, schema):
    """
    Создает таблицу в Supabase через REST API
    
    Args:
        table_name (str): Имя таблицы
        schema (str): SQL схема таблицы
    
    Returns:
        bool: True если таблица создана успешно, False в противном случае
    """
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    }
    
    # Проверяем существование таблицы
    check_url = f"{supabase_url}/rest/v1/{table_name}?limit=1"
    try:
        response = requests.get(check_url, headers=headers)
        if response.status_code == 200:
            print(f"Таблица {table_name} уже существует.")
            return True
    except Exception as e:
        print(f"Ошибка при проверке таблицы {table_name}: {e}")
    
    # Создаем таблицу через REST API
    try:
        # Используем API Supabase для выполнения SQL
        sql_url = f"{supabase_url}/rest/v1/rpc/exec_sql"
        payload = {"query": schema}
        
        response = requests.post(sql_url, headers=headers, json=payload)
        
        # Если API exec_sql не существует, пробуем альтернативный метод
        if response.status_code == 404:
            print(f"API exec_sql не найден. Пробуем создать таблицу напрямую...")
            
            # Создаем таблицу через POST запрос
            # Для tracked_accounts
            if table_name == "tracked_accounts":
                create_url = f"{supabase_url}/rest/v1/tracked_accounts"
                payload = {
                    "twitter_username": "test_user",
                    "guild_id": "test_guild",
                    "channel_id": "test_channel"
                }
                response = requests.post(create_url, headers=headers, json=payload)
                
                # Если таблица успешно создана или существует, удаляем тестовую запись
                if response.status_code in [201, 409]:
                    print(f"Таблица {table_name} создана успешно.")
                    # Удаляем тестовую запись
                    delete_url = f"{supabase_url}/rest/v1/tracked_accounts?twitter_username=eq.test_user"
                    requests.delete(delete_url, headers=headers)
                    return True
            
            # Для cached_tweets
            elif table_name == "cached_tweets":
                create_url = f"{supabase_url}/rest/v1/cached_tweets"
                payload = {
                    "tweet_id": "test_id",
                    "twitter_username": "test_user"
                }
                response = requests.post(create_url, headers=headers, json=payload)
                
                # Если таблица успешно создана или существует, удаляем тестовую запись
                if response.status_code in [201, 409]:
                    print(f"Таблица {table_name} создана успешно.")
                    # Удаляем тестовую запись
                    delete_url = f"{supabase_url}/rest/v1/cached_tweets?tweet_id=eq.test_id"
                    requests.delete(delete_url, headers=headers)
                    return True
        
        elif response.status_code == 200:
            print(f"Таблица {table_name} создана успешно.")
            return True
        else:
            print(f"Ошибка при создании таблицы {table_name}: {response.text}")
            return False
            
    except Exception as e:
        print(f"Ошибка при создании таблицы {table_name}: {e}")
        return False

def main():
    """
    Создает необходимые таблицы в базе данных Supabase
    """
    print("Создание таблиц в базе данных Supabase...")
    
    # Проверяем наличие учетных данных Supabase
    if not supabase_url or not supabase_key:
        print("Ошибка: Не найдены учетные данные Supabase в файле .env")
        print("Убедитесь, что в файле .env указаны SUPABASE_URL и SUPABASE_KEY")
        return
    
    # SQL-запрос для создания таблицы tracked_accounts
    create_tracked_accounts_table = """
    CREATE TABLE IF NOT EXISTS tracked_accounts (
        id SERIAL PRIMARY KEY,
        twitter_username TEXT NOT NULL,
        guild_id TEXT NOT NULL,
        channel_id TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(twitter_username, guild_id)
    );
    """
    
    # SQL-запрос для создания таблицы cached_tweets
    create_cached_tweets_table = """
    CREATE TABLE IF NOT EXISTS cached_tweets (
        id SERIAL PRIMARY KEY,
        tweet_id TEXT NOT NULL,
        twitter_username TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        UNIQUE(tweet_id)
    );
    """
    
    # Создаем таблицы
    print("Создание таблицы tracked_accounts...")
    create_table("tracked_accounts", create_tracked_accounts_table)
    
    print("\nСоздание таблицы cached_tweets...")
    create_table("cached_tweets", create_cached_tweets_table)
    
    print("\nПроцесс создания таблиц завершен.")
    print("Теперь вы можете запустить бота с помощью команды:")
    print("./run_bot.sh" if os.name != 'nt' else "run_bot.bat")

if __name__ == "__main__":
    main() 