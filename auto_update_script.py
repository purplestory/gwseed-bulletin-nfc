#!/usr/bin/env python3
"""
정기적으로 최신 주보를 확인하고 자동으로 업데이트하는 스크립트
"""

import sqlite3
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json
import os

def get_latest_bulletin_from_website():
    """교회 웹사이트에서 최신 주보 정보 가져오기"""
    try:
        url = "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 최신 주보 링크 찾기 (공지가 아닌 일반 게시물)
        latest_post = None
        for post in soup.select("tbody tr:not(.bo_notice)"):
            link_tag = post.select_one("td.td_subject a")
            if link_tag and 'href' in link_tag.attrs:
                href = str(link_tag['href'])
                if 'wr_id=' in href and 'weekly' in href:
                    if not href.startswith('http'):
                        href = "https://www.godswillseed.or.kr" + href
                    
                    # wr_id 추출
                    wr_id_match = re.search(r'wr_id=(\d+)', href)
                    wr_id = wr_id_match.group(1) if wr_id_match else None
                    
                    # 제목 추출
                    title = link_tag.get_text(strip=True)
                    
                    latest_post = {
                        'url': href,
                        'wr_id': wr_id,
                        'title': title,
                        'timestamp': datetime.now().isoformat()
                    }
                    break
        
        return latest_post
        
    except Exception as e:
        print(f"최신 주보 정보 가져오기 실패: {e}")
        return None

def get_latest_bulletin_from_db():
    """데이터베이스에서 최신 주보 정보 가져오기"""
    conn = sqlite3.connect('weekly_posts.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT wr_id, title FROM weekly_posts ORDER BY wr_id DESC LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            return {
                'wr_id': result[0],
                'title': result[1]
            }
        return None
        
    except Exception as e:
        print(f"데이터베이스에서 최신 주보 가져오기 실패: {e}")
        return None
    finally:
        conn.close()

def add_new_bulletin_to_db(bulletin_info):
    """새로운 주보를 데이터베이스에 추가"""
    conn = sqlite3.connect('weekly_posts.db')
    cursor = conn.cursor()
    
    try:
        wr_id = bulletin_info['wr_id']
        title = bulletin_info['title']
        url = bulletin_info['url']
        
        # 날짜 추출
        date_match = re.search(r'(\d{4})년\s*(\d{1,2})월\s*(\d{1,2})일', title)
        if date_match:
            year, month, day = date_match.groups()
            post_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        else:
            post_date = datetime.now().strftime("%Y-%m-%d")
        
        # 데이터베이스에 삽입
        cursor.execute("""
            INSERT INTO weekly_posts (wr_id, title, url, created_at, image_paths, ocr_data)
            VALUES (?, ?, ?, ?, '', '')
        """, (wr_id, title, url, post_date))
        
        conn.commit()
        print(f"✅ 새로운 주보가 데이터베이스에 추가되었습니다: {title}")
        return True
        
    except Exception as e:
        print(f"❌ 주보 추가 실패: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_latest_bulletin_file(bulletin_info):
    """최신 주보 정보를 파일에 저장"""
    try:
        with open('latest_bulletin.json', 'w', encoding='utf-8') as f:
            json.dump(bulletin_info, f, ensure_ascii=False, indent=2)
        print(f"✅ 최신 주보 정보 파일 업데이트: {bulletin_info['title']}")
        return True
    except Exception as e:
        print(f"❌ 파일 업데이트 실패: {e}")
        return False

def check_and_update_latest_bulletin():
    """최신 주보 확인 및 업데이트"""
    print("🔍 교회 웹사이트에서 최신 주보 확인 중...")
    
    # 웹사이트에서 최신 주보 정보 가져오기
    website_latest = get_latest_bulletin_from_website()
    if not website_latest:
        print("❌ 웹사이트에서 최신 주보 정보를 가져올 수 없습니다.")
        return False
    
    print(f"📋 웹사이트 최신 주보: {website_latest['title']} (wr_id: {website_latest['wr_id']})")
    
    # 데이터베이스에서 최신 주보 정보 가져오기
    db_latest = get_latest_bulletin_from_db()
    if db_latest:
        print(f"📋 데이터베이스 최신 주보: {db_latest['title']} (wr_id: {db_latest['wr_id']})")
    else:
        print("📋 데이터베이스에 주보가 없습니다.")
    
    # 새로운 주보인지 확인
    if not db_latest or int(website_latest['wr_id']) > int(db_latest['wr_id']):
        print("🆕 새로운 주보가 발견되었습니다!")
        
        # 데이터베이스에 추가
        if add_new_bulletin_to_db(website_latest):
            # 최신 주보 정보 파일 업데이트
            update_latest_bulletin_file(website_latest)
            
            print("🎉 새로운 주보가 성공적으로 추가되었습니다!")
            print("📝 다음 단계: scraper.py를 실행하여 이미지 다운로드 및 OCR 처리를 진행하세요.")
            return True
        else:
            print("❌ 새로운 주보 추가에 실패했습니다.")
            return False
    else:
        print("✅ 이미 최신 주보가 데이터베이스에 있습니다.")
        # 최신 주보 정보 파일 업데이트
        update_latest_bulletin_file(website_latest)
        return True

if __name__ == "__main__":
    check_and_update_latest_bulletin() 