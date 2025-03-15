#!/bin/bash

# Директория, где находится бот
BOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BOT_DIR"

# Активация виртуальной среды
source .venv/bin/activate

# Запуск бота с перенаправлением вывода в файл
echo "Запуск Discord бота TweetSync..."
echo "Для остановки нажмите Ctrl+C"
echo "Лог сохраняется в файл bot.log"

# Запускаем в фоне с перенаправлением вывода
python run_bot.py > bot.log 2>&1 