# Руководство по настройке Twitter-Discord бота

## Шаг 1: Настройка Discord бота

1. **Создайте нового Discord бота:**
   - Перейдите на [Discord Developer Portal](https://discord.com/developers/applications)
   - Нажмите на кнопку "New Application" в правом верхнем углу
   - Введите имя (например "TweetSync Bot") и нажмите "Create"
   - В левом меню выберите "Bot"
   - Нажмите "Add Bot" и подтвердите действие
   - **ВАЖНО**: В настройках бота включите опцию "Message Content Intent" в разделе "Privileged Gateway Intents"
   - Нажмите "Save Changes"
   - Нажмите кнопку "Reset Token" (или "View Token" если это новый бот) и скопируйте токен

2. **Настройте файл .env:**
   - Откройте файл `.env`
   - Замените значение `DISCORD_TOKEN` на скопированный токен:
     ```
     DISCORD_TOKEN=ваш_новый_токен
     ```

3. **Создайте ссылку для приглашения бота:**
   - В Discord Developer Portal перейдите в "OAuth2" -> "URL Generator"
   - В разделе "Scopes" выберите "bot" и "applications.commands" 
   - В разделе "Bot Permissions" выберите:
     - Read Messages/View Channels
     - Send Messages
     - Embed Links
     - Read Message History
   - Скопируйте сгенерированный URL и откройте его в браузере
   - Выберите "Guild Install" (установка на сервер)
   - Выберите сервер, на который хотите добавить бота, и нажмите "Authorize"

## Шаг 2: Настройка Supabase (база данных)

1. **Зарегистрируйтесь на Supabase:**
   - Перейдите на [Supabase](https://supabase.com/)
   - Создайте аккаунт или войдите в существующий
   - Создайте новый проект

2. **Получите учетные данные Supabase:**
   - В проекте перейдите в "Settings" -> "API"
   - Скопируйте "URL" и "anon/public key"
   - Обновите файл `.env`:
     ```
     SUPABASE_URL=ваш_supabase_url
     SUPABASE_KEY=ваш_supabase_key
     ```

3. **Создайте таблицы в базе данных:**
   - Запустите скрипт создания таблиц:
     ```
     python create_tables.py
     ```
   - Убедитесь, что скрипт успешно выполнился

## Шаг 3: Настройка Twitter API

1. **Получите доступ к Twitter API:**
   - Перейдите на [Twitter Developer Portal](https://developer.twitter.com/)
   - Создайте аккаунт разработчика и проект
   - Создайте приложение в проекте

2. **Получите ключи доступа:**
   - Получите Bearer Token, API Key и API Secret
   - Обновите файл `.env`:
     ```
     TWITTER_BEARER_TOKEN=ваш_bearer_token
     TWITTER_API_KEY=ваш_api_key
     TWITTER_API_SECRET=ваш_api_secret
     ```

## Шаг 4: Запуск бота

1. **Установите зависимости:**
   ```
   pip install -r requirements.txt
   ```

2. **Запустите бота:**
   - На Windows:
     ```
     python run_bot.py
     ```
   - На Mac/Linux:
     ```
     python run_bot.py
     ```

3. **Убедитесь, что бот запустился:**
   - В консоли должно появиться сообщение о подключении к Discord
   - В Discord введите команду `!ping`
   - Бот должен ответить "Pong!"

## Шаг 5: Использование бота

1. **Добавление Twitter аккаунта для отслеживания:**
   ```
   !track username
   ```
   Например: `!track elonmusk`

2. **Просмотр списка отслеживаемых аккаунтов:**
   ```
   !list
   ```

3. **Удаление Twitter аккаунта из отслеживаемых:**
   ```
   !untrack username
   ```

4. **Справка по командам:**
   ```
   !tweetsync_help
   ```

## Устранение неполадок

### Проблема с токеном Discord (Invalid Form Body)

Если вы получаете ошибку "Invalid Form Body":

1. Создайте полностью нового бота в Discord Developer Portal
2. Получите новый токен и обновите .env
3. Убедитесь, что включены необходимые интенты в настройках бота
4. Используйте свежесгенерированную ссылку для приглашения бота на сервер

### Проблема с базой данных

Если вы видите ошибки, связанные с базой данных:

1. Проверьте, что учетные данные Supabase верны
2. Запустите скрипт для создания таблиц:
   ```
   python create_tables.py
   ```
3. Проверьте права доступа к базе данных

### Проблема с Twitter API

Если твиты не загружаются:

1. Проверьте, что учетные данные Twitter API верны
2. Убедитесь, что у вас есть доступ к Twitter API v2
3. Проверьте, не исчерпан ли лимит запросов к API 