# Загрузка проекта на GitHub и настройка автономной работы

В этом руководстве описано, как загрузить ваш Discord Twitter бот на GitHub и настроить его для автономной работы на сервере.

## 1. Создание репозитория на GitHub

1. Перейдите на [GitHub](https://github.com) и войдите в свою учетную запись.
2. Нажмите на кнопку "+" в правом верхнем углу и выберите "New repository".
3. Заполните информацию о репозитории:
   - Имя репозитория: `discord-twitter-bot` (или другое по вашему выбору)
   - Описание: `Discord бот для отслеживания и отправки твитов в каналы Discord`
   - Выберите "Public" или "Private" в зависимости от ваших предпочтений
   - НЕ отмечайте "Initialize this repository with a README"
4. Нажмите "Create repository"

## 2. Загрузка кода в репозиторий

### Инициализация Git и первый коммит

```bash
# Перейдите в директорию вашего бота
cd /путь/к/discord-twitter-bot

# Инициализируйте Git репозиторий
git init

# Добавьте все файлы в индекс
git add .

# Создайте первый коммит
git commit -m "Initial commit"

# Добавьте удаленный репозиторий
git remote add origin https://github.com/ваш-username/discord-twitter-bot.git

# Загрузите код в репозиторий
git push -u origin main
```

Примечание: Если ваша ветка называется `master`, а не `main`, используйте:
```bash
git push -u origin master
```

## 3. Настройка автономной работы на сервере

### Вариант 1: Запуск на VPS (Linux)

1. Подключитесь к вашему серверу по SSH:
   ```bash
   ssh username@your-server-ip
   ```

2. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш-username/discord-twitter-bot.git
   cd discord-twitter-bot
   ```

3. Запустите скрипт деплоя для systemd:
   ```bash
   python deploy.py --systemd
   ```

4. Установите systemd сервис:
   ```bash
   sudo ./start_bot_service.sh
   ```

### Вариант 2: Запуск на VPS с использованием Docker

1. Подключитесь к вашему серверу по SSH.
2. Установите Docker, если его еще нет:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh
   ```

3. Склонируйте репозиторий:
   ```bash
   git clone https://github.com/ваш-username/discord-twitter-bot.git
   cd discord-twitter-bot
   ```

4. Создайте и настройте файл .env:
   ```bash
   cp .env.example .env
   nano .env  # Отредактируйте файл, добавив ваши токены
   ```

5. Соберите и запустите Docker-контейнер:
   ```bash
   docker build -t discord-twitter-bot .
   docker run -d --name discord-bot --restart always discord-twitter-bot
   ```

### Вариант 3: Настройка через GitHub Actions

Для автоматического деплоя при обновлении кода в репозитории:

1. Запустите скрипт для настройки GitHub Actions:
   ```bash
   python deploy.py --github
   ```

2. Добавьте секреты в ваш GitHub репозиторий:
   - Перейдите в Settings > Secrets > New repository secret
   - Добавьте следующие секреты:
     - `HOST`: IP-адрес вашего сервера
     - `USERNAME`: имя пользователя SSH
     - `SSH_KEY`: приватный SSH-ключ для аутентификации

3. Затем при каждом push в ветку main бот будет автоматически обновляться на сервере.

## 4. Обновление бота

### Ручное обновление

```bash
# На сервере
cd /путь/к/discord-twitter-bot
git pull
sudo systemctl restart discord-twitter-bot  # если используете systemd
```

### Обновление через Docker

```bash
# На сервере
cd /путь/к/discord-twitter-bot
git pull
docker build -t discord-twitter-bot .
docker stop discord-bot
docker rm discord-bot
docker run -d --name discord-bot --restart always discord-twitter-bot
```

## 5. Мониторинг и логи

### Для systemd

```bash
# Проверка статуса
sudo systemctl status discord-twitter-bot

# Просмотр логов
sudo journalctl -u discord-twitter-bot -f
```

### Для Docker

```bash
# Проверка статуса
docker ps

# Просмотр логов
docker logs -f discord-bot
```

## Дополнительные ресурсы

- [GitHub Documentation](https://docs.github.com)
- [Docker Documentation](https://docs.docker.com)
- [Systemd Documentation](https://systemd.io) 