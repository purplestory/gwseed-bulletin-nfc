from flask import Flask, redirect, request
import requests
from bs4 import BeautifulSoup
import re

app = Flask(__name__)

def get_latest_bulletin_url():
    """교회 주보 게시판에서 최신 주보 URL을 가져옴"""
    try:
        # 교회 주보 게시판 URL
        base_url = "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly"
        
        # 페이지 요청
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 최신 주보 링크 찾기 (첫 번째 일반 게시물)
        post_links = soup.select("tbody tr:not(.bo_notice) td.td_subject a")
        
        if post_links:
            latest_link = str(post_links[0].get('href', ''))
            if latest_link and not latest_link.startswith('http'):
                latest_link = "https://www.godswillseed.or.kr" + latest_link
            return latest_link if latest_link else None
        
        return None
        
    except Exception as e:
        print(f"최신 주보 URL 가져오기 실패: {e}")
        return None

@app.route('/')
def nfc_redirect():
    """NFC 태그로 접근 시 최신 주보로 리다이렉트"""
    latest_url = get_latest_bulletin_url()
    
    if latest_url:
        return redirect(latest_url, code=302)
    else:
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