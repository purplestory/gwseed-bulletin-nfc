from flask import Flask, redirect, request
import requests
from bs4 import BeautifulSoup
import re
import time

app = Flask(__name__)

def get_latest_bulletin_url():
    """교회 주보 게시판에서 최신 주보 URL을 가져옴"""
    try:
        # 교회 주보 게시판 URL
        base_url = "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly"
        
        # 간단한 헤더 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive'
        }
        
        # 간단한 요청
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 모든 링크에서 wr_id 패턴 찾기
        all_links = soup.find_all('a', href=True)
        weekly_links = []
        
        for link in all_links:
            href = str(link.get('href', ''))
            if 'wr_id=' in href and 'weekly' in href:
                weekly_links.append(href)
        
        if weekly_links:
            # 첫 번째 링크가 최신 주보
            latest_link = weekly_links[0]
            if not latest_link.startswith('http'):
                latest_link = "https://www.godswillseed.or.kr" + latest_link
            return latest_link
        
        return None
        
    except Exception as e:
        print(f"스크래핑 실패: {e}")
        return None

@app.route('/')
def nfc_redirect():
    """NFC 태그로 접근 시 최신 주보로 리다이렉트"""
    latest_url = get_latest_bulletin_url()
    
    if latest_url:
        return redirect(latest_url, code=302)
    else:
        # 실패 시 주보 게시판으로 리다이렉트
        return redirect("https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly", code=302)

@app.route('/health')
def health_check():
    """헬스 체크용 엔드포인트"""
    return {"status": "healthy", "service": "nfc_redirect"}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004) 