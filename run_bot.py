#!/usr/bin/env python3
import os
import sys
import subprocess
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("tweetsync_bot")

def get_python_path():
    """Get the path to python in the virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join(".venv", "Scripts", "python")
    else:  # Unix/Linux/Mac
        return os.path.join(".venv", "bin", "python")

def check_env_file():
    """Check if .env file exists and has required variables"""
    if not os.path.exists(".env"):
        logger.error(".env file not found")
        return False
    
    with open(".env", "r") as f:
        env_content = f.read()
    
    required_vars = ["DISCORD_TOKEN", "TWITTER_BEARER_TOKEN", "SUPABASE_URL", "SUPABASE_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if var + "=" not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    logger.info("Environment file check passed")
    return True

def main():
    """Main function to run the Discord bot"""
    logger.info("Начало запуска Discord бота TweetSync...")
    
    # Проверка env файла
    if not check_env_file():
        logger.error("Проверка .env файла не пройдена")
        sys.exit(1)
    
    python_path = get_python_path()
    logger.info(f"Используется Python из: {python_path}")
    
    print("Запуск Discord бота TweetSync...")
    print("Для остановки нажмите Ctrl+C")
    
    # Run the bot with verbose output
    try:
        # Adding environment variable for debug mode
        env = os.environ.copy()
        env["DISCORD_DEBUG"] = "1"
        
        logger.info("Запуск бота с расширенным логированием...")
        subprocess.run([python_path, "bot.py"], check=True, env=env)
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем.")
    except subprocess.SubprocessError as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 