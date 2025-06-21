from flask import Flask, redirect, request
import requests
import json
import os

app = Flask(__name__)

def get_latest_bulletin_url():
    """저장된 최신 주보 URL을 가져옴"""
    try:
        # 현재 도메인에서 API 호출
        base_url = request.host_url.rstrip('/')
        api_url = f"{base_url}/api/get-latest"
        
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        
        data = response.json()
        return data.get('url')
        
    except Exception as e:
        print(f"API 호출 실패: {e}")
        return None

@app.route('/')
def nfc_redirect():
    """NFC 태그로 접근 시 최신 주보로 리다이렉트"""
    latest_url = get_latest_bulletin_url()
    
    if latest_url and 'wr_id=' in latest_url:
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