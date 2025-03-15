import discord
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("tweetsync")

def create_embed(title, description, color=discord.Color.blue(), fields=None, footer=None, thumbnail=None):
    """
    Create a Discord embed
    
    Args:
        title (str): Embed title
        description (str): Embed description
        color (discord.Color, optional): Embed color. Defaults to discord.Color.blue().
        fields (list, optional): List of field dicts with name, value, inline keys. Defaults to None.
        footer (str, optional): Footer text. Defaults to None.
        thumbnail (str, optional): Thumbnail URL. Defaults to None.
    
    Returns:
        discord.Embed: The created embed
    """
    embed = discord.Embed(title=title, description=description, color=color)
    
    if fields:
        for field in fields:
            embed.add_field(
                name=field["name"],
                value=field["value"],
                inline=field.get("inline", False)
            )
    
    if footer:
        embed.set_footer(text=footer)
    
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    
    return embed

def create_tweet_embed(tweet, username):
    """
    Create a Discord embed for a tweet
    
    Args:
        tweet (dict): Tweet data
        username (str): Twitter username
    
    Returns:
        discord.Embed: The created embed
    """
    tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
    
    # Format metrics
    likes = tweet.public_metrics['like_count'] if hasattr(tweet, 'public_metrics') else 0
    retweets = tweet.public_metrics['retweet_count'] if hasattr(tweet, 'public_metrics') else 0
    
    # Ограничиваем длину текста твита (Discord ограничивает description до 4096 символов)
    tweet_text = tweet.text
    if len(tweet_text) > 4000:
        tweet_text = tweet_text[:4000] + "..."
    
    # Create embed
    embed = discord.Embed(
        title=f"New Tweet from @{username}"[:256],  # Ограничиваем длину заголовка
        description=tweet_text,
        color=discord.Color.blue(),
        url=tweet_url
    )
    
    # Add metrics as fields
    embed.add_field(name="❤️ Likes", value=str(likes), inline=True)
    embed.add_field(name="🔄 Retweets", value=str(retweets), inline=True)
    
    # Add timestamp
    if hasattr(tweet, 'created_at'):
        embed.timestamp = tweet.created_at
    
    # Add Twitter logo as thumbnail
    embed.set_thumbnail(url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")
    
    # Add footer
    embed.set_footer(text="Twitter", icon_url="https://abs.twimg.com/icons/apple-touch-icon-192x192.png")
    
    return embed

def check_permissions(ctx, permission):
    """
    Check if a user has the required permission
    
    Args:
        ctx (discord.ext.commands.Context): Command context
        permission (str): Permission to check
    
    Returns:
        bool: True if user has permission, False otherwise
    """
    if ctx.author.guild_permissions.administrator:
        return True
    
    if permission == "manage_channels" and ctx.author.guild_permissions.manage_channels:
        return True
    
    if permission == "manage_messages" and ctx.author.guild_permissions.manage_messages:
        return True
    
    return False 