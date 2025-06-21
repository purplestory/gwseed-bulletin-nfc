from flask import Flask, redirect, request
import os

app = Flask(__name__)

# 최신 주보 URL (환경 변수 또는 기본값)
LATEST_BULLETIN_URL = os.environ.get(
    'LATEST_BULLETIN_URL', 
    "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly&wr_id=732"
)

@app.route('/')
def nfc_redirect():
    """NFC 태그로 접근 시 최신 주보로 리다이렉트"""
    print(f"🔄 리다이렉트: {LATEST_BULLETIN_URL}")
    return redirect(LATEST_BULLETIN_URL, code=302)

@app.route('/health')
def health_check():
    """헬스 체크용 엔드포인트"""
    return {
        "status": "healthy", 
        "service": "nfc_redirect",
        "latest_bulletin": LATEST_BULLETIN_URL,
        "environment": "production" if os.environ.get('VERCEL') else "local"
    }

@app.route('/update/<int:wr_id>')
def update_latest_bulletin(wr_id):
    """최신 주보 URL 업데이트 (관리자용)"""
    global LATEST_BULLETIN_URL
    new_url = f"https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly&wr_id={wr_id}"
    LATEST_BULLETIN_URL = new_url
    
    return {
        "status": "updated",
        "new_url": new_url,
        "message": f"최신 주보가 wr_id={wr_id}로 업데이트되었습니다."
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004) 