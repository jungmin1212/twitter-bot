#!/usr/bin/env python3
"""엑셀 → SQLite 마이그레이션"""
import sqlite3
import pandas as pd

DB_PATH = "tweets.db"
EXCEL_PATH = "Grass_Auto_Tweets.xlsx"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS tweets (
            id INTEGER PRIMARY KEY,
            language TEXT NOT NULL,
            tweet_text TEXT NOT NULL,
            last_posted TEXT
        )
    ''')
    conn.commit()
    return conn

def migrate_excel_to_db(excel_path):
    df = pd.read_excel(excel_path)
    conn = init_db()
    
    conn.execute("DELETE FROM tweets")
    
    for _, row in df.iterrows():
        conn.execute(
            "INSERT INTO tweets (id, language, tweet_text, last_posted) VALUES (?, ?, ?, ?)",
            (row['ID'], row['Language'], row['Tweet_Text'], None if pd.isna(row['Last_Posted']) else row['Last_Posted'])
        )
    
    conn.commit()
    conn.close()
    print(f"✅ {len(df)}개 데이터 마이그레이션 완료")

if __name__ == "__main__":
    migrate_excel_to_db(EXCEL_PATH)
