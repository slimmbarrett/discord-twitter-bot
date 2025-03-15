# ВНИМАНИЕ! Необходимо получить новый токен бота. Текущий токен неработоспособен.

# Инструкция по получению нового токена Discord бота

## Проблема
В логах вашего бота видна ошибка: `Improper token has been passed.`

Это означает, что токен бота в файле `.env` неправильный или устарел.

## Шаги для получения нового токена

1. **Создайте нового бота (рекомендуется)**

   Самый надежный способ - создать полностью нового бота:
   
   1. Откройте [Discord Developer Portal](https://discord.com/developers/applications)
   2. Нажмите на кнопку "New Application" в правом верхнем углу
   3. Введите имя (например "TweetSync Bot") и нажмите "Create"
   4. В левом меню выберите "Bot"
   5. Нажмите "Add Bot" и подтвердите действие
   6. **ВАЖНО**: В настройках бота включите опцию "Message Content Intent" в разделе "Privileged Gateway Intents"
   7. Нажмите кнопку "Reset Token" (или "View Token" если это новый бот)
   8. Скопируйте новый токен

2. **Обновите файл .env**

   Откройте файл `.env` и замените строку:
   
   ```
   DISCORD_TOKEN=MTM1MDAzODc4Njc1NDQ3ODE1MQ.GTv_jT.9jiQhOtrGgcOkEaLB_A25WRZae-vZkEd4FxNcI
   ```
   
   На:
   
   ```
   DISCORD_TOKEN=ваш_новый_токен
   ```
   
   Сохраните файл.

3. **Создайте ссылку для приглашения бота**

   1. В Discord Developer Portal перейдите в раздел "OAuth2" → "URL Generator"
   2. В "Scopes" выберите "bot" и "applications.commands"
   3. В "Bot Permissions" выберите следующие права:
      - Read Messages/View Channels
      - Send Messages
      - Embed Links
      - Read Message History
   4. Скопируйте сгенерированный URL и используйте его для добавления бота на свой сервер

## Исправление проблемы с Supabase

В логах также видна ошибка подключения к базе данных. Запустите скрипт для создания таблиц:

```
python create_tables.py
```

Если проблема сохраняется, вам может потребоваться обновить учетные данные Supabase или создать новую базу данных.
