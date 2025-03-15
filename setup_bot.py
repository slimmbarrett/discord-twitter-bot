#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
import venv

def check_python_version():
    """Check if Python version is 3.9 or higher"""
    if sys.version_info < (3, 9):
        print("Ошибка: Требуется Python 3.9 или выше.")
        sys.exit(1)
    print("✅ Проверка версии Python пройдена")

def create_virtual_env():
    """Create a virtual environment"""
    if os.path.exists(".venv"):
        print("✅ Виртуальное окружение уже существует")
        return True
    
    print("Создание виртуального окружения...")
    try:
        venv.create(".venv", with_pip=True)
        print("✅ Виртуальное окружение успешно создано")
        return True
    except Exception as e:
        print(f"❌ Не удалось создать виртуальное окружение: {e}")
        return False

def get_pip_path():
    """Get the path to pip in the virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join(".venv", "Scripts", "pip")
    else:  # Unix/Linux/Mac
        return os.path.join(".venv", "bin", "pip")

def get_python_path():
    """Get the path to python in the virtual environment"""
    if os.name == 'nt':  # Windows
        return os.path.join(".venv", "Scripts", "python")
    else:  # Unix/Linux/Mac
        return os.path.join(".venv", "bin", "python")

def install_dependencies():
    """Install dependencies from requirements.txt in the virtual environment"""
    print("Установка зависимостей...")
    pip_path = get_pip_path()
    
    try:
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Зависимости успешно установлены")
        return True
    except subprocess.SubprocessError as e:
        print(f"❌ Не удалось установить зависимости: {e}")
        return False

def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("Создание файла .env из .env.example...")
            shutil.copy(".env.example", ".env")
            print("✅ Файл .env создан")
            print("⚠️ Пожалуйста, отредактируйте файл .env и добавьте ваши API ключи и токены")
        else:
            print("❌ Файл .env.example не найден")
            return False
    else:
        print("✅ Файл .env уже существует")
    return True

def check_discord_token():
    """Check if Discord token is set in .env file"""
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("DISCORD_TOKEN=") and line.strip() != "DISCORD_TOKEN=your_discord_bot_token":
                    print("✅ Токен Discord установлен")
                    return True
        print("❌ Токен Discord не установлен в файле .env")
        return False
    return False

def setup_discord_token():
    """Set up Discord token"""
    if not os.path.exists(".env"):
        print("❌ Файл .env не найден")
        return False
    
    token = input("Введите токен вашего Discord бота: ")
    
    if not token:
        print("❌ Токен не предоставлен")
        return False
    
    # Read the .env file
    with open(".env", "r") as f:
        lines = f.readlines()
    
    # Update the Discord token
    with open(".env", "w") as f:
        for line in lines:
            if line.startswith("DISCORD_TOKEN="):
                f.write(f"DISCORD_TOKEN={token}\n")
            else:
                f.write(line)
    
    print("✅ Токен Discord установлен")
    return True

def create_run_script():
    """Create a run script to activate the virtual environment and run the Discord bot"""
    python_path = get_python_path()
    
    if os.name == 'nt':  # Windows
        with open("run_bot.bat", "w") as f:
            f.write(f'@echo off\n')
            f.write(f'echo Запуск Discord бота TweetSync...\n')
            f.write(f'"{python_path}" bot.py\n')
        
        print("✅ Создан скрипт run_bot.bat")
    else:  # Unix/Linux/Mac
        with open("run_bot.sh", "w") as f:
            f.write(f'#!/bin/bash\n')
            f.write(f'echo "Запуск Discord бота TweetSync..."\n')
            f.write(f'"{python_path}" bot.py\n')
        
        # Make the script executable
        os.chmod("run_bot.sh", 0o755)
        print("✅ Создан скрипт run_bot.sh")

def main():
    """Main setup function"""
    print("Настройка Discord бота TweetSync")
    print("==============================")
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    if not create_virtual_env():
        print("Пожалуйста, создайте виртуальное окружение вручную и попробуйте снова.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("Пожалуйста, установите зависимости вручную и попробуйте снова.")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("Пожалуйста, создайте файл .env вручную на основе файла .env.example.")
    
    # Check Discord token
    if not check_discord_token():
        print("\nВам нужно настроить токен Discord бота.")
        print("Вы можете создать бота на портале разработчиков Discord:")
        print("https://discord.com/developers/applications")
        print("1. Создайте новое приложение")
        print("2. Перейдите в раздел 'Bot'")
        print("3. Нажмите 'Add Bot'")
        print("4. Скопируйте токен и вставьте его ниже")
        
        setup = input("\nХотите настроить токен Discord сейчас? (y/n): ")
        if setup.lower() == "y":
            setup_discord_token()
        else:
            print("Пожалуйста, установите токен Discord вручную в файле .env.")
    
    # Create run script
    create_run_script()
    
    print("\nНастройка завершена!")
    if os.name == 'nt':  # Windows
        print("Для запуска бота выполните: run_bot.bat")
    else:  # Unix/Linux/Mac
        print("Для запуска бота выполните: ./run_bot.sh")
    
    print("\nДля добавления бота на ваш сервер Discord используйте следующую ссылку:")
    print("https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=2147483648&scope=bot")
    print("(Замените YOUR_CLIENT_ID на ID вашего приложения Discord)")

if __name__ == "__main__":
    main() 