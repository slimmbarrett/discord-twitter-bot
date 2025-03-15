#!/usr/bin/env python3
import os
import sys
import subprocess
from dotenv import load_dotenv
import logging

# Настройка логирования с экранированием специальных символов
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("fix_zsh")

def main():
    """
    Функция для запуска бота Discord с исправлением ошибки zsh
    """
    logger.info("Запуск бота Discord TweetSync с исправлением ошибки zsh...")
    
    # Загрузить переменные окружения
    load_dotenv()
    
    # Активировать виртуальное окружение Python, если оно не активировано
    python_executable = sys.executable
    if '.venv' not in python_executable:
        venv_python = os.path.join('.venv', 'bin', 'python')
        if os.path.exists(venv_python):
            python_executable = venv_python
    
    logger.info(f"Используется Python: {python_executable}")
    
    try:
        # Запустить бота напрямую из Python, а не через subprocess
        # Это обходит проблему с оболочкой zsh
        logger.info("Бот запускается...")
        
        # Импорт bot.py напрямую
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Установка флага отладки
        os.environ["DISCORD_DEBUG"] = "1"
        
        # Запуск бота напрямую
        import bot
        
    except Exception as e:
        logger.error(f"Произошла ошибка при запуске бота: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 