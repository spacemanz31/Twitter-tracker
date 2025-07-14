import tweepy
from textblob import TextBlob
from datetime import datetime
from telegram import Bot
import os

BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")  # Replace or set in .env

keywords = "bitcoin OR ethereum OR crypto OR $SOL OR $DOGE OR $BTC"
bot = Bot(token=TELEGRAM_TOKEN)

class SentimentStream(tweepy.StreamingClient):
    def on_tweet(self, tweet):
        if tweet.referenced_tweets: return  # Skip retweets/replies
        analysis = TextBlob(tweet.text)
        score = analysis.sentiment.polarity
        sentiment = "Positive" if score > 0.1 else "Negative" if score < -0.1 else "Neutral"
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] {sentiment} ({score:.2f})\n{tweet.text}"
        print(msg)
        if CHAT_ID:
            bot.send_message(chat_id=CHAT_ID, text=msg)

def run_tracker():
    stream = SentimentStream(bearer_token=BEARER_TOKEN)
    rules = stream.get_rules().data
    if rules:
        stream.delete_rules([rule.id for rule in rules])
    stream.add_rules(tweepy.StreamRule(keywords))
    stream.filter(tweet_fields=["text"])

if __name__ == "__main__":
    run_tracker()
