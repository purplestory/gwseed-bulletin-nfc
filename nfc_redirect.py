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
        
        # 더 강력한 헤더 설정
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'DNT': '1'
        }
        
        # 세션 사용으로 더 안정적인 연결
        session = requests.Session()
        session.headers.update(headers)
        
        # 첫 번째 요청으로 세션 설정
        print("🔍 교회 웹사이트에 접속 중...")
        response = session.get(base_url, timeout=20)
        response.raise_for_status()
        
        print(f"✅ 응답 상태: {response.status_code}")
        print(f"📄 응답 크기: {len(response.text)} bytes")
        
        # 응답 내용 확인
        if "자동등록방지" in response.text or "보안절차" in response.text:
            print("❌ 보안절차 감지됨")
            return None
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 최신 주보 링크 찾기 (다양한 방법 시도)
        post_links = soup.select("tbody tr:not(.bo_notice) td.td_subject a")
        
        if not post_links:
            # 대안 방법: wr_id 패턴으로 찾기
            all_links = soup.find_all('a', href=True)
            post_links = [link for link in all_links if 'wr_id=' in str(link.get('href', ''))]
        
        if post_links:
            latest_link = str(post_links[0].get('href', ''))
            if latest_link and not latest_link.startswith('http'):
                latest_link = "https://www.godswillseed.or.kr" + latest_link
            
            print(f"🎯 최신 주보 URL: {latest_link}")
            return latest_link if latest_link else None
        
        print("❌ 주보 링크를 찾을 수 없음")
        return None
        
    except Exception as e:
        print(f"❌ 최신 주보 URL 가져오기 실패: {e}")
        return None

@app.route('/')
def nfc_redirect():
    """NFC 태그로 접근 시 최신 주보로 리다이렉트"""
    latest_url = get_latest_bulletin_url()
    
    if latest_url:
        print(f"🔄 리다이렉트: {latest_url}")
        return redirect(latest_url, code=302)
    else:
        print("⚠️  리다이렉트 실패, fallback 페이지 표시")
        return """
        <html>
        <head>
            <title>높은뜻씨앗이되어교회 주보</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body { 
                    font-family: 'Noto Sans KR', sans-serif; 
                    text-align: center; 
                    padding: 50px; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    min-height: 100vh;
                    margin: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }
                .container {
                    background: rgba(255,255,255,0.1);
                    padding: 40px;
                    border-radius: 20px;
                    backdrop-filter: blur(10px);
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                }
                h1 { margin-bottom: 20px; }
                .loading {
                    display: inline-block;
                    width: 20px;
                    height: 20px;
                    border: 3px solid rgba(255,255,255,.3);
                    border-radius: 50%;
                    border-top-color: #fff;
                    animation: spin 1s ease-in-out infinite;
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
                .manual-link {
                    margin-top: 30px;
                    padding: 15px 30px;
                    background: rgba(255,255,255,0.2);
                    border-radius: 10px;
                    text-decoration: none;
                    color: white;
                    display: inline-block;
                    transition: all 0.3s ease;
                }
                .manual-link:hover {
                    background: rgba(255,255,255,0.3);
                    transform: translateY(-2px);
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏛️ 높은뜻씨앗이되어교회</h1>
                <p>최신 주보를 불러오는 중입니다...</p>
                <div class="loading"></div>
                <div style="margin-top: 30px;">
                    <a href="https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly" 
                       class="manual-link">
                        📋 주보 게시판으로 이동
                    </a>
                </div>
            </div>
            <script>
                // 3초 후 자동으로 주보 게시판으로 이동
                setTimeout(function() {
                    window.location.href = 'https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly';
                }, 3000);
            </script>
        </body>
        </html>
        """

@app.route('/health')
def health_check():
    """헬스 체크용 엔드포인트"""
    return {"status": "healthy", "service": "nfc_redirect"}

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004) 