#!/bin/bash

# Директория, где находится бот
BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BOT_DIR"

# Проверить, установлен ли Python 3
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 не установлен. Пожалуйста, установите Python 3."
    exit 1
fi

# Проверить, активирована ли виртуальная среда
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Активация виртуальной среды..."
    if [ -d ".venv" ]; then
        source .venv/bin/activate
    else
        echo "Виртуальная среда не найдена. Создаю новую..."
        python3 -m venv .venv
        source .venv/bin/activate
        
        # Установка зависимостей
        echo "Установка зависимостей..."
        pip install -r requirements.txt
    fi
fi

# Запускаем фиксированный Python-скрипт
echo "Запуск Discord бота..."
python fix_zsh_error.py

# Если скрипт завершится с ошибкой
if [ $? -ne 0 ]; then
    echo "Бот завершился с ошибкой. Проверьте лог файл bot.log"
    echo "Проверьте настройки Discord и подключение к Discord серверу."
fi 