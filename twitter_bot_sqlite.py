#!/usr/bin/env python3
import sqlite3
import tweepy
from datetime import datetime
import time
import os

class TwitterBotSQLite:
    def __init__(self, db_path, api_key, api_secret, access_token, access_secret, bearer_token):
        self.db_path = db_path
        
        self.client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_secret
        )
        
        try:
            self.client.get_me()
            print("✅ API 인증 성공")
        except Exception as e:
            print(f"❌ API 인증 실패: {e}")
            raise
    
    def get_available_tweet(self, language):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            SELECT id, tweet_text 
            FROM tweets 
            WHERE language = ? 
            AND (last_posted IS NULL OR julianday('now') - julianday(last_posted) >= 5)
            ORDER BY RANDOM()
            LIMIT 1
        ''', (language,))
        
        result = c.fetchone()
        conn.close()
        
        if result:
            return result[0], result[1]
        return None, None
    
    def update_last_posted(self, tweet_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "UPDATE tweets SET last_posted = ? WHERE id = ?",
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), tweet_id)
        )
        conn.commit()
        conn.close()
    
    def post_tweet(self, tweet_text):
        try:
            self.client.create_tweet(text=tweet_text)
            print(f"✅ 트윗 게시: {tweet_text[:50]}...")
            return True
        except Exception as e:
            print(f"❌ 트윗 실패: {e}")
            return False
    
    def run_daily(self):
        languages = ['Korean', 'English', 'Spanish']
        posted_count = 0
        
        print(f"\n{'='*50}")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}")
        
        for lang in languages:
            tweet_id, tweet_text = self.get_available_tweet(lang)
            
            if tweet_text:
                print(f"\n🌍 {lang}")
                success = self.post_tweet(tweet_text)
                
                if success:
                    self.update_last_posted(tweet_id)
                    posted_count += 1
                    
                    if lang != 'Spanish':
                        print("⏳ 1분 대기...")
                        time.sleep(60)
            else:
                print(f"⚠️ {lang}: 사용 가능한 트윗 없음")
        
        print(f"\n✅ {posted_count}개 트윗 완료" if posted_count > 0 else "\n⚠️ 게시된 트윗 없음")


if __name__ == "__main__":
    API_KEY = os.getenv("TWITTER_API_KEY")
    API_SECRET = os.getenv("TWITTER_API_SECRET")
    ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN")
    ACCESS_SECRET = os.getenv("TWITTER_ACCESS_SECRET")
    BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")
    
    if not all([API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET, BEARER_TOKEN]):
        raise ValueError("모든 트위터 API 키가 환경변수에 설정되어야 합니다")
    
    DB_PATH = os.getenv("DB_PATH", "tweets.db")
    
    bot = TwitterBotSQLite(DB_PATH, API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET, BEARER_TOKEN)
    bot.run_daily()