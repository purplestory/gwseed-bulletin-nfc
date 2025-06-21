from flask import Flask, redirect, request
import requests
import json
import os

app = Flask(__name__)

# 환경 변수에서 최신 주보 URL 가져오기 (기본값: wr_id=732)
LATEST_BULLETIN_URL = os.environ.get(
    'LATEST_BULLETIN_URL', 
    "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly&wr_id=732"
)

def get_latest_bulletin_url():
    """저장된 최신 주보 URL을 가져옴 (API 실패 시 환경 변수 사용)"""
    try:
        # 현재 도메인에서 API 호출
        base_url = request.host_url.rstrip('/')
        api_url = f"{base_url}/api/get-latest"
        
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        url = data.get('url')
        
        # wr_id가 포함된 URL인지 확인
        if url and 'wr_id=' in url:
            return url
            
    except Exception as e:
        print(f"API 호출 실패: {e}")
    
    # API 실패 시 환경 변수 값 반환
    return LATEST_BULLETIN_URL

@app.route('/')
def nfc_redirect():
    """NFC 태그로 접근 시 최신 주보로 리다이렉트"""
    latest_url = get_latest_bulletin_url()
    return redirect(latest_url, code=302)

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
    
    # API도 함께 업데이트
    try:
        base_url = request.host_url.rstrip('/')
        api_url = f"{base_url}/api/update-latest"
        requests.post(api_url, timeout=5)
    except:
        pass
    
    return {
        "status": "updated",
        "new_url": new_url,
        "message": f"최신 주보가 wr_id={wr_id}로 업데이트되었습니다.",
        "note": "환경 변수도 함께 업데이트하는 것을 권장합니다."
    }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004) 