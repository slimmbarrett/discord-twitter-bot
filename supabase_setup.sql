-- Create tracked_accounts table
CREATE TABLE IF NOT EXISTS tracked_accounts (
    id SERIAL PRIMARY KEY,
    twitter_username TEXT NOT NULL,
    guild_id TEXT NOT NULL,
    channel_id TEXT NOT NULL,
    webhook_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(twitter_username, guild_id)
);

-- Create cached_tweets table
CREATE TABLE IF NOT EXISTS cached_tweets (
    id SERIAL PRIMARY KEY,
    tweet_id TEXT NOT NULL UNIQUE,
    twitter_username TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_tracked_accounts_guild_id ON tracked_accounts(guild_id);
CREATE INDEX IF NOT EXISTS idx_tracked_accounts_twitter_username ON tracked_accounts(twitter_username);
CREATE INDEX IF NOT EXISTS idx_cached_tweets_tweet_id ON cached_tweets(tweet_id);
CREATE INDEX IF NOT EXISTS idx_cached_tweets_twitter_username ON cached_tweets(twitter_username);

-- Create RLS policies for security
ALTER TABLE tracked_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE cached_tweets ENABLE ROW LEVEL SECURITY;

-- Create policy to allow authenticated users to read tracked_accounts
CREATE POLICY tracked_accounts_select_policy ON tracked_accounts 
    FOR SELECT USING (auth.role() = 'authenticated');

-- Create policy to allow authenticated users to insert into tracked_accounts
CREATE POLICY tracked_accounts_insert_policy ON tracked_accounts 
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Create policy to allow authenticated users to update tracked_accounts
CREATE POLICY tracked_accounts_update_policy ON tracked_accounts 
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Create policy to allow authenticated users to delete from tracked_accounts
CREATE POLICY tracked_accounts_delete_policy ON tracked_accounts 
    FOR DELETE USING (auth.role() = 'authenticated');

-- Create policy to allow authenticated users to read cached_tweets
CREATE POLICY cached_tweets_select_policy ON cached_tweets 
    FOR SELECT USING (auth.role() = 'authenticated');

-- Create policy to allow authenticated users to insert into cached_tweets
CREATE POLICY cached_tweets_insert_policy ON cached_tweets 
    FOR INSERT WITH CHECK (auth.role() = 'authenticated');

-- Create policy to allow authenticated users to update cached_tweets
CREATE POLICY cached_tweets_update_policy ON cached_tweets 
    FOR UPDATE USING (auth.role() = 'authenticated');

-- Create policy to allow authenticated users to delete from cached_tweets
CREATE POLICY cached_tweets_delete_policy ON cached_tweets 
    FOR DELETE USING (auth.role() = 'authenticated'); 