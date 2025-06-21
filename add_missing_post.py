import sqlite3
from datetime import datetime

def add_missing_post():
    """누락된 wr_id=732 주보를 수동으로 추가"""
    conn = sqlite3.connect('weekly_posts.db')
    cursor = conn.cursor()
    
    # 기존 데이터 확인
    cursor.execute("SELECT * FROM weekly_posts WHERE wr_id = 732")
    existing = cursor.fetchone()
    
    if existing:
        print("wr_id=732 주보가 이미 존재합니다.")
        conn.close()
        return
    
    # 새 주보 데이터 추가
    post_data = {
        'wr_id': 732,
        'title': '2025년 6월 22일 주보',
        'author': '김선민목사',
        'created_at': '2025-06-21',
        'views': 10,
        'image_count': 4,
        'image_paths': '20250621_page_01.jpeg,20250621_page_02.jpeg,20250621_page_03.jpeg,20250621_page_04.jpeg',
        'ocr_data': None  # OCR 데이터는 나중에 추가
    }
    
    try:
        cursor.execute("""
            INSERT INTO weekly_posts (wr_id, title, author, created_at, views, image_count, image_paths, ocr_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            post_data['wr_id'],
            post_data['title'],
            post_data['author'],
            post_data['created_at'],
            post_data['views'],
            post_data['image_count'],
            post_data['image_paths'],
            post_data['ocr_data']
        ))
        
        conn.commit()
        print(f"wr_id={post_data['wr_id']} 주보가 성공적으로 추가되었습니다.")
        
    except Exception as e:
        print(f"주보 추가 실패: {e}")
        conn.rollback()
    
    conn.close()

if __name__ == "__main__":
    add_missing_post() 