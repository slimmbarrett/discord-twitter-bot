FROM python:3.10-slim

WORKDIR /app

# Установка необходимых пакетов
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Копирование файлов проекта
COPY . .

# Установка зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# Добавление рабочим файлам разрешения на выполнение
RUN chmod +x fix_init.sh fix_zsh_error.py run_bot_fixed.sh

# Запуск бота при старте контейнера
CMD ["python", "fix_zsh_error.py"] 