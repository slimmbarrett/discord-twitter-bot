import os
import tweepy
from dotenv import load_dotenv
from db import Database
import ssl

# Load environment variables
load_dotenv()

# Twitter API credentials
bearer_token = os.getenv("TWITTER_BEARER_TOKEN")
api_key = os.getenv("TWITTER_API_KEY")
api_secret = os.getenv("TWITTER_API_SECRET")

# Отключаем проверку SSL-сертификатов
ssl._create_default_https_context = ssl._create_unverified_context

class TwitterClient:
    def __init__(self):
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret
        )
        self.db = Database()
    
    def get_user_by_username(self, username):
        """
        Get Twitter user information by username
        
        Args:
            username (str): Twitter username
        
        Returns:
            dict: User information
        """
        try:
            user = self.client.get_user(username=username)
            return user.data
        except tweepy.TweepyException as e:
            print(f"Error getting user {username}: {e}")
            return None
    
    def get_recent_tweets(self, username, max_results=10):
        """
        Get recent tweets from a user
        
        Args:
            username (str): Twitter username
            max_results (int): Maximum number of tweets to retrieve
        
        Returns:
            list: List of tweets
        """
        try:
            # First get the user ID
            user = self.get_user_by_username(username)
            if not user:
                return []
            
            # Then get their recent tweets
            tweets = self.client.get_users_tweets(
                id=user.id,
                max_results=max_results,
                tweet_fields=['created_at', 'text', 'public_metrics']
            )
            
            return tweets.data if tweets.data else []
        except tweepy.TweepyException as e:
            print(f"Error getting tweets for {username}: {e}")
            return []
    
    def create_filtered_stream_rules(self, usernames):
        """
        Create filtered stream rules for tracking Twitter accounts
        
        Args:
            usernames (list): List of Twitter usernames to track
        
        Returns:
            list: List of created rules
        """
        try:
            # First, delete all existing rules
            rules = self.client.get_rules()
            if rules.data:
                rule_ids = [rule.id for rule in rules.data]
                self.client.delete_rules(rule_ids)
            
            # Create new rules for each username
            rules = []
            for username in usernames:
                rules.append(f"from:{username}")
            
            if rules:
                response = self.client.add_rules(rules)
                return response.data
            return []
        except tweepy.TweepyException as e:
            print(f"Error creating stream rules: {e}")
            return []
    
    def format_tweet_for_discord(self, tweet, username):
        """
        Format a tweet for Discord display
        
        Args:
            tweet (dict): Tweet data
            username (str): Twitter username
        
        Returns:
            str: Formatted message
        """
        tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
        
        # Format metrics
        likes = tweet.public_metrics['like_count'] if hasattr(tweet, 'public_metrics') else 0
        retweets = tweet.public_metrics['retweet_count'] if hasattr(tweet, 'public_metrics') else 0
        
        # Create formatted message
        message = f"**New Tweet from @{username}**\n\n"
        message += f"{tweet.text}\n\n"
        message += f"❤️ {likes} | 🔄 {retweets}\n"
        message += f"🔗 {tweet_url}"
        
        return message 