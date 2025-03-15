import os
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test_bot')

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Проверка токена
if not TOKEN or TOKEN == "ВСТАВЬТЕ_НОВЫЙ_ТОКЕН_СЮДА":
    logger.error("Ошибка: Токен не найден или не был изменен в файле .env")
    logger.error("Получите новый токен в Discord Developer Portal и обновите файл .env")
    exit(1)

# Базовая настройка бота с минимальными интентами
intents = discord.Intents.default()
intents.message_content = True  # Нужно включить в Discord Developer Portal

# Создание бота
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f"Бот успешно подключился как {bot.user.name}")
    logger.info(f"ID бота: {bot.user.id}")
    logger.info(f"Подключен к серверам: {[guild.name for guild in bot.guilds]}")
    
@bot.command(name="ping")
async def ping(ctx):
    """Простая команда для проверки работы бота"""
    await ctx.send("Pong!")

# Запуск бота
try:
    logger.info("Запуск тестового бота...")
    bot.run(TOKEN)
except discord.LoginFailure as e:
    logger.error(f"Ошибка входа: {e}")
    logger.error("Это может быть вызвано недействительным токеном. Получите новый токен в Discord Developer Portal.")
    
    if "Invalid Form Body" in str(e):
        logger.error("Ошибка 'Invalid Form Body' обычно связана с неправильным форматом токена.")
        logger.error("Проверьте, что токен скопирован полностью и не содержит лишних пробелов или переносов строк.")
    
except Exception as e:
    logger.error(f"Ошибка при запуске бота: {e}") 