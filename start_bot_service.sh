#!/bin/bash

# Скрипт для настройки и запуска Discord Twitter бота как службы systemd на Linux-сервере

# Проверяем, запущен ли скрипт от имени root
if [ "$(id -u)" -ne 0 ]; then
    echo "Этот скрипт должен быть запущен от имени root или с sudo"
    exit 1
fi

# Определяем текущего пользователя, если запущено через sudo
if [ -n "$SUDO_USER" ]; then
    ACTUAL_USER=$SUDO_USER
else
    ACTUAL_USER=$(whoami)
fi

# Определяем путь к директории скрипта
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Создаем файл службы systemd
echo "Создание файла службы systemd..."
cat > /etc/systemd/system/discord-twitter-bot.service << EOL
[Unit]
Description=Discord Twitter Bot
After=network.target

[Service]
User=$ACTUAL_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/.venv/bin/python $SCRIPT_DIR/fix_zsh_error.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOL

# Перезагружаем настройки systemd
echo "Перезагрузка настроек systemd..."
systemctl daemon-reload

# Включаем службу для запуска при загрузке
echo "Включение службы для запуска при загрузке..."
systemctl enable discord-twitter-bot

# Запускаем службу
echo "Запуск службы discord-twitter-bot..."
systemctl start discord-twitter-bot

# Проверяем статус
echo "Статус службы:"
systemctl status discord-twitter-bot

echo "
------------------------------------
Установка службы завершена!

Полезные команды:
- Проверить статус: sudo systemctl status discord-twitter-bot
- Перезапустить бот: sudo systemctl restart discord-twitter-bot
- Остановить бот: sudo systemctl stop discord-twitter-bot
- Просмотреть логи: sudo journalctl -u discord-twitter-bot -f
------------------------------------
" 