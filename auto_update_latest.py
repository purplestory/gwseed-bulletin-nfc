import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import re

def get_latest_bulletin_info():
    """교회 웹사이트에서 최신 주보 정보 가져오기"""
    try:
        url = "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 최신 주보 링크 찾기
        all_links = soup.find_all('a', href=True)
        weekly_links = []
        
        for link in all_links:
            href = str(link.get('href', ''))
            if 'wr_id=' in href and 'weekly' in href:
                weekly_links.append(href)
        
        if weekly_links:
            latest_link = weekly_links[0]
            if not latest_link.startswith('http'):
                latest_link = "https://www.godswillseed.or.kr" + latest_link
            
            # wr_id 추출
            wr_id_match = re.search(r'wr_id=(\d+)', latest_link)
            wr_id = wr_id_match.group(1) if wr_id_match else None
            
            return {
                'url': latest_link,
                'wr_id': wr_id,
                'timestamp': datetime.now().isoformat()
            }
        
        return None
        
    except Exception as e:
        print(f"최신 주보 정보 가져오기 실패: {e}")
        return None

def update_latest_bulletin_file():
    """최신 주보 정보를 파일에 저장"""
    info = get_latest_bulletin_info()
    
    if info:
        with open('latest_bulletin.json', 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        print(f"✅ 최신 주보 정보 업데이트: {info['url']}")
        return True
    else:
        print("❌ 최신 주보 정보 업데이트 실패")
        return False

if __name__ == "__main__":
    update_latest_bulletin_file() 