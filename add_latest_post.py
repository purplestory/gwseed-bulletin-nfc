import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime

def add_latest_post():
    """최신 주보(wr_id=732)를 데이터베이스에 추가"""
    
    # 데이터베이스 연결
    conn = sqlite3.connect('weekly_posts.db')
    cursor = conn.cursor()
    
    try:
        # 최신 주보 정보
        wr_id = 732
        title = "2025년 6월 22일 주보"
        url = f"https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly&wr_id={wr_id}"
        
        print(f"📋 추가할 주보 정보:")
        print(f"  - wr_id: {wr_id}")
        print(f"  - 제목: {title}")
        print(f"  - URL: {url}")
        
        # 기존 데이터 확인
        cursor.execute("SELECT * FROM posts WHERE wr_id = ?", (wr_id,))
        existing = cursor.fetchone()
        
        if existing:
            print(f"⚠️  이미 존재하는 게시물입니다: {existing}")
            return
        
        # 주보 페이지에서 정보 추출
        print(f"🔍 주보 페이지에서 정보 추출 중...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 날짜 추출
        date_match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', title)
        if date_match:
            year, month, day = date_match.groups()
            post_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        else:
            post_date = datetime.now().strftime("%Y-%m-%d")
        
        print(f"  - 날짜: {post_date}")
        
        # 데이터베이스에 삽입
        cursor.execute("""
            INSERT INTO posts (wr_id, title, url, post_date, created_at, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (wr_id, title, url, post_date))
        
        conn.commit()
        print(f"✅ 주보가 성공적으로 추가되었습니다!")
        
        # 추가된 데이터 확인
        cursor.execute("SELECT * FROM posts WHERE wr_id = ?", (wr_id,))
        added_post = cursor.fetchone()
        print(f"📊 추가된 데이터: {added_post}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    add_latest_post() 