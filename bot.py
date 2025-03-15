import os
import discord
from discord.ext import commands, tasks
import asyncio
import logging
from dotenv import load_dotenv
import ssl
import traceback
import sys

from db import Database
from twitter_client import TwitterClient
from utils import create_embed, create_tweet_embed, check_permissions, logger

# Настройка более подробного логирования, если включен Debug режим
if os.environ.get("DISCORD_DEBUG", "0") == "1":
    discord.utils.setup_logging(level=logging.DEBUG)
    logger.setLevel(logging.DEBUG)
    logger.debug("Discord DEBUG режим включен")

# Load environment variables
load_dotenv()
logger.info("Переменные окружения загружены")

# Discord bot token
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    logger.error("Discord token not found in .env file")
    raise ValueError("DISCORD_TOKEN not found in environment variables")
else:
    token_prefix = TOKEN[:7] + "..." if len(TOKEN) > 10 else "Invalid token"
    logger.info(f"Discord токен загружен: {token_prefix}")

# Bot configuration
intents = discord.Intents.default()
intents.message_content = True  # Убедитесь, что этот интент включен в Discord Developer Portal!

# Отключаем привилегированные интенты, которые не включены в Developer Portal
intents.members = False  # Если этот интент вам нужен, включите его в Developer Portal
intents.presences = False  # Если этот интент вам нужен, включите его в Developer Portal

# Отладочная информация об интентах
logger.info(f"Настроены интенты: message_content={intents.message_content}, members={intents.members}, presences={intents.presences}")
bot = commands.Bot(command_prefix="!", intents=intents)

# Initialize database and Twitter client
db = Database()
twitter = TwitterClient()

# Полностью отключаем проверку SSL-сертификатов
ssl._create_default_https_context = ssl._create_unverified_context

@bot.event
async def on_ready():
    """Event triggered when the bot is ready"""
    logger.info(f"{bot.user.name} has connected to Discord!")
    logger.info(f"Bot ID: {bot.user.id}")
    logger.info(f"Guilds: {[guild.name for guild in bot.guilds]}")
    
    # Start background tasks
    try:
        check_new_tweets.start()
        logger.info("Background task check_new_tweets started successfully")
    except Exception as e:
        logger.error(f"Error starting background task: {e}")
        logger.error(traceback.format_exc())
    
    # Set bot status
    try:
        await bot.change_presence(activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="Twitter"
        ))
        logger.info("Bot status set successfully")
    except Exception as e:
        logger.error(f"Error setting bot status: {e}")
        logger.error(traceback.format_exc())

@bot.event
async def on_error(event, *args, **kwargs):
    """Event triggered when an error occurs"""
    logger.error(f"Discord error in {event}: {sys.exc_info()[1]}")
    logger.error(traceback.format_exc())

# Добавляем простую команду для тестирования
@bot.command(name="ping")
async def ping(ctx):
    """Simple command to test if the bot is working"""
    try:
        await ctx.send("Pong!")
        logger.info("Ping command executed successfully")
    except Exception as e:
        logger.error(f"Error executing ping command: {e}")

@tasks.loop(minutes=5)
async def check_new_tweets():
    """Background task to check for new tweets from tracked accounts"""
    try:
        # Get all tracked accounts
        tracked_accounts = db.get_tracked_accounts()
        
        if not tracked_accounts:
            return
        
        # Group accounts by guild_id and channel_id
        accounts_by_channel = {}
        for account in tracked_accounts:
            guild_id = account["guild_id"]
            channel_id = account["channel_id"]
            username = account["twitter_username"]
            
            # Skip accounts tracked via webhook
            if guild_id == "webhook" or channel_id == "webhook":
                continue
            
            key = f"{guild_id}:{channel_id}"
            if key not in accounts_by_channel:
                accounts_by_channel[key] = []
            
            accounts_by_channel[key].append(username)
        
        # Check for new tweets for each channel
        for key, usernames in accounts_by_channel.items():
            guild_id, channel_id = key.split(":")
            channel = bot.get_channel(int(channel_id))
            
            if not channel:
                logger.warning(f"Channel {channel_id} not found")
                continue
            
            for username in usernames:
                # Get recent tweets
                tweets = twitter.get_recent_tweets(username, max_results=5)
                
                for tweet in tweets:
                    # Skip if tweet is already cached
                    if db.is_tweet_cached(tweet.id):
                        continue
                    
                    # Cache the tweet
                    db.cache_tweet(tweet.id, username)
                    
                    try:
                        # Send tweet to Discord
                        embed = create_tweet_embed(tweet, username)
                        await channel.send(embed=embed)
                        logger.info(f"Sent tweet {tweet.id} from {username} to channel {channel_id}")
                    except discord.HTTPException as e:
                        logger.error(f"HTTP error sending tweet {tweet.id}: {e}")
                    except Exception as e:
                        logger.error(f"Error sending tweet {tweet.id}: {e}")
                    
                    # Add a small delay to avoid rate limits
                    await asyncio.sleep(1)
    
    except Exception as e:
        logger.error(f"Error in check_new_tweets task: {e}")

@check_new_tweets.before_loop
async def before_check_new_tweets():
    """Wait until the bot is ready before starting the task"""
    await bot.wait_until_ready()

@bot.command(name="track")
async def track_account(ctx, username: str = None):
    """
    Track a Twitter account and send new tweets to the current channel
    
    Args:
        ctx (discord.ext.commands.Context): Command context
        username (str, optional): Twitter username to track
    """
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
    """
    Stop tracking a Twitter account
    
    Args:
        ctx (discord.ext.commands.Context): Command context
        username (str, optional): Twitter username to untrack
    """
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
    """
    List all tracked Twitter accounts for this server
    
    Args:
        ctx (discord.ext.commands.Context): Command context
    """
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
    """
    Show help information for the bot
    
    Args:
        ctx (discord.ext.commands.Context): Command context
    """
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
    if isinstance(error, commands.CommandNotFound):
        return
    
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Отсутствует обязательный аргумент: {error.param.name}")
        return
    
    logger.error(f"Command error: {error}")
    await ctx.send(f"Произошла ошибка при выполнении команды: {str(error)[:1000]}")

# Run the bot
if __name__ == "__main__":
    try:
        logger.info("Запуск Discord бота")
        bot.run(TOKEN, log_handler=None)
    except discord.LoginFailure as e:
        logger.error(f"Ошибка авторизации Discord: {e}")
        logger.error("Проверьте ваш токен бота в файле .env")
        if "Invalid Form Body" in str(e):
            logger.error("Ошибка 'Invalid Form Body' обычно означает, что токен неверен или устарел.")
            logger.error("Создайте новый токен в Discord Developer Portal: https://discord.com/developers/applications")
        sys.exit(1)
    except discord.PrivilegedIntentsRequired as e:
        logger.error(f"Требуются привилегированные интенты, которые не включены: {e}")
        logger.error("Включите необходимые интенты в Discord Developer Portal -> Bot -> Privileged Gateway Intents")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Необработанная ошибка: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1) 