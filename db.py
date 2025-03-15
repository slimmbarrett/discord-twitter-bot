import os
import ssl
import requests
import json
from dotenv import load_dotenv

# Отключаем проверку SSL-сертификатов
ssl._create_default_https_context = ssl._create_unverified_context

# Загружаем переменные окружения
load_dotenv()

class Database:
    def __init__(self):
        # Получаем учетные данные Supabase из переменных окружения
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        # Проверяем наличие учетных данных
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Не найдены учетные данные Supabase. Проверьте переменные SUPABASE_URL и SUPABASE_KEY в файле .env")
        
        # Заголовки для запросов
        self.headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        # Создаем таблицы, если они не существуют
        self._create_tables()
    
    def _create_tables(self):
        """
        Создает необходимые таблицы в базе данных, если они не существуют
        """
        try:
            # Проверяем существование таблиц
            tracked_accounts_url = f"{self.supabase_url}/rest/v1/tracked_accounts?limit=1"
            cached_tweets_url = f"{self.supabase_url}/rest/v1/cached_tweets?limit=1"
            
            # Отправляем запросы для проверки существования таблиц
            requests.get(tracked_accounts_url, headers=self.headers)
            requests.get(cached_tweets_url, headers=self.headers)
            
            # Если запросы не вызвали ошибок, значит таблицы существуют
            print("Таблицы в базе данных уже существуют.")
        except Exception as e:
            print(f"Ошибка при создании таблиц: {e}")
            print("Таблицы могут уже существовать или у вас нет прав на их создание.")
            print("Если бот не работает, запустите скрипт create_tables.py для создания таблиц.")
    
    def add_tracked_account(self, twitter_username, guild_id, channel_id):
        """
        Добавляет аккаунт Twitter в список отслеживаемых
        
        Args:
            twitter_username (str): Имя пользователя Twitter
            guild_id (str): ID сервера Discord
            channel_id (str): ID канала Discord
        
        Returns:
            dict: Результат операции
        """
        try:
            # Проверяем, существует ли уже такая запись
            check_url = f"{self.supabase_url}/rest/v1/tracked_accounts?twitter_username=eq.{twitter_username}&guild_id=eq.{guild_id}"
            response = requests.get(check_url, headers=self.headers)
            
            if response.status_code == 200 and len(response.json()) > 0:
                # Запись уже существует
                existing_record = response.json()[0]
                
                # Если канал отличается, обновляем запись
                if existing_record["channel_id"] != str(channel_id):
                    update_url = f"{self.supabase_url}/rest/v1/tracked_accounts?id=eq.{existing_record['id']}"
                    payload = {"channel_id": str(channel_id)}
                    
                    response = requests.patch(update_url, headers=self.headers, json=payload)
                    
                    if response.status_code == 200:
                        return {"message": f"Аккаунт @{twitter_username} уже отслеживается, обновлен канал назначения."}
                    else:
                        return {"error": f"Ошибка при обновлении канала: {response.text}"}
                else:
                    return {"error": f"Аккаунт @{twitter_username} уже отслеживается в этом канале."}
            
            # Добавляем новую запись
            insert_url = f"{self.supabase_url}/rest/v1/tracked_accounts"
            payload = {
                "twitter_username": twitter_username,
                "guild_id": str(guild_id),
                "channel_id": str(channel_id)
            }
            
            response = requests.post(insert_url, headers=self.headers, json=payload)
            
            if response.status_code == 201:
                return {"message": f"Аккаунт @{twitter_username} добавлен для отслеживания."}
            else:
                return {"error": f"Ошибка при добавлении аккаунта: {response.text}"}
                
        except Exception as e:
            return {"error": f"Ошибка при добавлении аккаунта: {str(e)}"}
    
    def remove_tracked_account(self, twitter_username, guild_id):
        """
        Удаляет аккаунт Twitter из списка отслеживаемых
        
        Args:
            twitter_username (str): Имя пользователя Twitter
            guild_id (str): ID сервера Discord
        
        Returns:
            bool: True если аккаунт успешно удален, False в противном случае
        """
        try:
            delete_url = f"{self.supabase_url}/rest/v1/tracked_accounts?twitter_username=eq.{twitter_username}&guild_id=eq.{guild_id}"
            
            # Сначала проверяем, существует ли запись
            response = requests.get(delete_url, headers=self.headers)
            
            if response.status_code != 200 or len(response.json()) == 0:
                return False
            
            # Удаляем запись
            response = requests.delete(delete_url, headers=self.headers)
            
            return response.status_code == 204
            
        except Exception as e:
            print(f"Ошибка при удалении аккаунта: {e}")
            return False
    
    def get_tracked_accounts(self, guild_id=None):
        """
        Получает список отслеживаемых аккаунтов Twitter
        
        Args:
            guild_id (str, optional): ID сервера Discord для фильтрации
        
        Returns:
            list: Список отслеживаемых аккаунтов
        """
        try:
            if guild_id:
                url = f"{self.supabase_url}/rest/v1/tracked_accounts?guild_id=eq.{guild_id}"
            else:
                url = f"{self.supabase_url}/rest/v1/tracked_accounts"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            print(f"Ошибка при получении списка отслеживаемых аккаунтов: {e}")
            return []
    
    def is_tweet_cached(self, tweet_id):
        """
        Проверяет, был ли твит уже обработан
        
        Args:
            tweet_id (str): ID твита
        
        Returns:
            bool: True если твит уже обработан, False в противном случае
        """
        try:
            url = f"{self.supabase_url}/rest/v1/cached_tweets?tweet_id=eq.{tweet_id}"
            
            response = requests.get(url, headers=self.headers)
            
            return response.status_code == 200 and len(response.json()) > 0
            
        except Exception as e:
            print(f"Ошибка при проверке кэша твитов: {e}")
            return False
    
    def cache_tweet(self, tweet_id, twitter_username):
        """
        Добавляет твит в кэш обработанных твитов
        
        Args:
            tweet_id (str): ID твита
            twitter_username (str): Имя пользователя Twitter
        
        Returns:
            bool: True если твит успешно добавлен в кэш, False в противном случае
        """
        try:
            url = f"{self.supabase_url}/rest/v1/cached_tweets"
            
            payload = {
                "tweet_id": str(tweet_id),
                "twitter_username": twitter_username
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            
            return response.status_code == 201
            
        except Exception as e:
            print(f"Ошибка при добавлении твита в кэш: {e}")
            return False 