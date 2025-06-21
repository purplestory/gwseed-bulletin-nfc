import sqlite3
import os
from datetime import datetime

def init_database():
    """데이터베이스 초기화 및 테이블 생성"""
    conn = sqlite3.connect('weekly_posts.db')
    cursor = conn.cursor()
    
    # 기존 테이블 삭제 (재생성)
    cursor.execute('DROP TABLE IF EXISTS weekly_posts')
    
    # 새로운 테이블 생성
    cursor.execute('''
        CREATE TABLE weekly_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wr_id INTEGER UNIQUE NOT NULL,
            title TEXT NOT NULL,
            author TEXT,
            created_at TEXT,
            views INTEGER,
            image_count INTEGER,
            image_paths TEXT,
            ocr_data TEXT,
            created_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("데이터베이스 초기화 완료")

def insert_bulletin_data():
    """스크랩된 주보 데이터를 데이터베이스에 삽입"""
    conn = sqlite3.connect('weekly_posts.db')
    cursor = conn.cursor()
    
    # 스크랩된 주보 데이터 (scraper.py 결과 기반)
    bulletins = [
        {
            'wr_id': 729,
            'title': '2025년 6월 1일 주보',
            'author': '김선민목사',
            'created_at': '2025-05-31',
            'views': 274,
            'image_count': 4,
            'image_paths': '20250531_page_01.jpeg,20250531_page_02.jpeg,20250531_page_03.jpeg,20250531_page_04.jpeg'
        },
        {
            'wr_id': 730,
            'title': '2025년 6월 8일 주보',
            'author': '김선민목사',
            'created_at': '2025-06-07',
            'views': 255,
            'image_count': 4,
            'image_paths': '20250607_page_01.jpeg,20250607_page_02.jpeg,20250607_page_03.jpeg,20250607_page_04.jpeg'
        },
        {
            'wr_id': 731,
            'title': '2025년 6월 15일 주보',
            'author': '김선민목사',
            'created_at': '2025-06-14',
            'views': 277,
            'image_count': 5,
            'image_paths': '20250614_page_01.jpeg,20250614_page_02.jpeg,20250614_page_03.jpeg,20250614_page_04.jpeg,20250614_page_05.jpg'
        }
    ]
    
    for bulletin in bulletins:
        cursor.execute('''
            INSERT OR REPLACE INTO weekly_posts 
            (wr_id, title, author, created_at, views, image_count, image_paths)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            bulletin['wr_id'],
            bulletin['title'],
            bulletin['author'],
            bulletin['created_at'],
            bulletin['views'],
            bulletin['image_count'],
            bulletin['image_paths']
        ))
    
    conn.commit()
    conn.close()
    print("주보 데이터 삽입 완료")

if __name__ == '__main__':
    init_database()
    insert_bulletin_data()
    print("데이터베이스 설정 완료!") 