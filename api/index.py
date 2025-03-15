import os
import sys
import discord
import asyncio
import logging
from flask import Flask, request, jsonify
from threading import Thread
from dotenv import load_dotenv
import ssl

# Добавляем родительскую директорию в путь для импорта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем модули бота
from db import Database
from twitter_client import TwitterClient
from utils import create_embed, create_tweet_embed, check_permissions, logger

# Отключаем проверку SSL-сертификатов
ssl._create_default_https_context = ssl._create_unverified_context

# Загружаем переменные окружения
load_dotenv()

# Discord bot token
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    logger.error("Discord token not found in .env file")
    raise ValueError("DISCORD_TOKEN not found in environment variables")

# Настройка Flask
app = Flask(__name__)

# Настройка бота Discord
intents = discord.Intents.default()
intents.message_content = True
bot = discord.ext.commands.Bot(command_prefix="!", intents=intents)

# Инициализация базы данных и клиента Twitter
db = Database()
twitter = TwitterClient()

# Глобальная переменная для хранения бота
bot_instance = None

@app.route('/')
def home():
    """Главная страница"""
    return jsonify({
        "status": "online",
        "message": "TweetSync Discord Bot is running"
    })

@app.route('/health')
def health():
    """Проверка состояния бота"""
    global bot_instance
    
    if bot_instance and bot_instance.is_ready():
        guilds = [guild.name for guild in bot_instance.guilds]
        return jsonify({
            "status": "healthy",
            "bot_name": bot_instance.user.name,
            "bot_id": str(bot_instance.user.id),
            "guilds_count": len(guilds),
            "guilds": guilds
        })
    else:
        return jsonify({
            "status": "starting",
            "message": "Bot is starting or not connected"
        })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Обработка вебхуков от Twitter"""
    data = request.json
    
    # Здесь можно добавить логику обработки вебхуков
    logger.info(f"Received webhook: {data}")
    
    return jsonify({"status": "success"})

# Настройка бота Discord
@bot.event
async def on_ready():
    """Event triggered when the bot is ready"""
    logger.info(f"{bot.user.name} has connected to Discord!")
    logger.info(f"Bot ID: {bot.user.id}")
    logger.info(f"Guilds: {[guild.name for guild in bot.guilds]}")
    
    # Установка статуса бота
    try:
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Twitter for new tweets"
        ))
    except Exception as e:
        logger.error(f"Error setting bot presence: {e}")

@bot.command(name="ping")
async def ping(ctx):
    """Simple command to test if the bot is working"""
    try:
        await ctx.send("Pong!")
        logger.info("Ping command executed successfully")
    except Exception as e:
        logger.error(f"Error executing ping command: {e}")

@bot.command(name="track")
async def track_account(ctx, username: str = None):
    """Track a Twitter account and send new tweets to the current channel"""
    try:
        # Check permissions
        if not check_permissions(ctx, "manage_channels"):
            await ctx.send("Вам нужно разрешение 'Управление каналами' для использования этой команды.")
            return
        
        # Check if username is provided
        if not username:
            await ctx.send("Пожалуйста, укажите имя пользователя Twitter для отслеживания.")
            return
        
        # Remove @ if present
        if username.startswith("@"):
            username = username[1:]
        
        # Check if the Twitter account exists
        user = twitter.get_user_by_username(username)
        if not user:
            await ctx.send(f"Аккаунт Twitter @{username} не найден.")
            return
        
        # Add to tracked accounts
        result = db.add_tracked_account(username, ctx.guild.id, ctx.channel.id)
        
        if result and "error" in result:
            await ctx.send(result["error"])
            return
        
        # Send confirmation
        embed = create_embed(
            title="Аккаунт Twitter добавлен для отслеживания",
            description=f"Теперь отслеживаются твиты от @{username} в этом канале.",
            color=discord.Color.green(),
            thumbnail="https://abs.twimg.com/icons/apple-touch-icon-192x192.png"
        )
        
        await ctx.send(embed=embed)
        
        # Get and send the most recent tweet as a preview
        tweets = twitter.get_recent_tweets(username, max_results=1)
        if tweets:
            tweet = tweets[0]
            try:
                embed = create_tweet_embed(tweet, username)
                await ctx.send("Вот самый последний твит от этого аккаунта:", embed=embed)
            except discord.HTTPException as e:
                logger.error(f"HTTP error sending preview tweet: {e}")
                await ctx.send("Не удалось отобразить последний твит из-за ошибки Discord API.")
    except Exception as e:
        logger.error(f"Error in track_account command: {e}")
        await ctx.send(f"Произошла ошибка при выполнении команды: {str(e)[:1000]}")

@bot.command(name="untrack")
async def untrack_account(ctx, username: str = None):
    """Stop tracking a Twitter account"""
    try:
        # Check permissions
        if not check_permissions(ctx, "manage_channels"):
            await ctx.send("Вам нужно разрешение 'Управление каналами' для использования этой команды.")
            return
        
        # Check if username is provided
        if not username:
            await ctx.send("Пожалуйста, укажите имя пользователя Twitter для прекращения отслеживания.")
            return
        
        # Remove @ if present
        if username.startswith("@"):
            username = username[1:]
        
        # Remove from tracked accounts
        result = db.remove_tracked_account(username, ctx.guild.id)
        
        if not result:
            await ctx.send(f"Аккаунт Twitter @{username} не отслеживается на этом сервере.")
            return
        
        # Send confirmation
        embed = create_embed(
            title="Отслеживание аккаунта Twitter прекращено",
            description=f"Больше не отслеживаются твиты от @{username} на этом сервере.",
            color=discord.Color.red(),
            thumbnail="https://abs.twimg.com/icons/apple-touch-icon-192x192.png"
        )
        
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error in untrack_account command: {e}")
        await ctx.send(f"Произошла ошибка при выполнении команды: {str(e)[:1000]}")

@bot.command(name="list")
async def list_tracked_accounts(ctx):
    """List all tracked Twitter accounts for this server"""
    try:
        # Get tracked accounts for this guild
        accounts = db.get_tracked_accounts(ctx.guild.id)
        
        if not accounts:
            await ctx.send("На этом сервере не отслеживаются аккаунты Twitter.")
            return
        
        # Group accounts by channel
        accounts_by_channel = {}
        for account in accounts:
            channel_id = account["channel_id"]
            username = account["twitter_username"]
            
            if channel_id not in accounts_by_channel:
                accounts_by_channel[channel_id] = []
            
            accounts_by_channel[channel_id].append(username)
        
        # Create embed
        embed = create_embed(
            title="Отслеживаемые аккаунты Twitter",
            description=f"Аккаунты Twitter, отслеживаемые на сервере {ctx.guild.name}",
            color=discord.Color.blue(),
            thumbnail="https://abs.twimg.com/icons/apple-touch-icon-192x192.png"
        )
        
        # Add fields for each channel
        for channel_id, usernames in accounts_by_channel.items():
            channel = bot.get_channel(int(channel_id))
            channel_name = f"#{channel.name}" if channel else f"Канал {channel_id}"
            
            usernames_formatted = "\n".join([f"@{username}" for username in usernames])
            # Ограничиваем длину значения поля до 1024 символов (лимит Discord)
            if len(usernames_formatted) > 1024:
                usernames_formatted = usernames_formatted[:1020] + "..."
                
            embed.add_field(
                name=channel_name,
                value=usernames_formatted,
                inline=False
            )
        
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error in list_tracked_accounts command: {e}")
        await ctx.send(f"Произошла ошибка при выполнении команды: {str(e)[:1000]}")

@bot.command(name="tweetsync_help")
async def help_command(ctx):
    """Show help information for the bot"""
    try:
        embed = create_embed(
            title="TweetSync Bot - Справка",
            description="Команды для управления отслеживанием аккаунтов Twitter",
            color=discord.Color.blue(),
            thumbnail="https://abs.twimg.com/icons/apple-touch-icon-192x192.png",
            fields=[
                {
                    "name": "!track <username>",
                    "value": "Начать отслеживание аккаунта Twitter в текущем канале",
                    "inline": False
                },
                {
                    "name": "!untrack <username>",
                    "value": "Прекратить отслеживание аккаунта Twitter на этом сервере",
                    "inline": False
                },
                {
                    "name": "!list",
                    "value": "Показать все отслеживаемые аккаунты Twitter на этом сервере",
                    "inline": False
                },
                {
                    "name": "!ping",
                    "value": "Проверить, работает ли бот",
                    "inline": False
                },
                {
                    "name": "!tweetsync_help",
                    "value": "Показать это справочное сообщение",
                    "inline": False
                }
            ],
            footer="Примечание: Вам нужно разрешение 'Управление каналами' для отслеживания/прекращения отслеживания аккаунтов"
        )
        
        await ctx.send(embed=embed)
    except Exception as e:
        logger.error(f"Error in help_command: {e}")
        await ctx.send(f"Произошла ошибка при выполнении команды: {str(e)[:1000]}")

# Обработка ошибок команд
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.CommandNotFound):
        return
    
    if isinstance(error, discord.ext.commands.MissingRequiredArgument):
        await ctx.send(f"Отсутствует обязательный аргумент: {error.param.name}")
        return
    
    logger.error(f"Command error: {error}")
    await ctx.send(f"Произошла ошибка при выполнении команды: {str(error)[:1000]}")

# Функция для запуска бота в отдельном потоке
def run_bot():
    global bot_instance
    bot_instance = bot
    
    try:
        logger.info("Starting Discord bot...")
        bot.run(TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid Discord token")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

# Запуск бота в отдельном потоке при запуске через Vercel
bot_thread = Thread(target=run_bot)
bot_thread.daemon = True
bot_thread.start()

# Для локального тестирования
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True) 