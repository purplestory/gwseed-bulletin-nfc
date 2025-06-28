#!/usr/bin/env python3
"""
정기적으로 최신 주보를 확인하고 자동으로 업데이트하는 스크립트
"""

import requests
from bs4 import BeautifulSoup, Tag
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

def get_latest_bulletin_from_file():
    """파일에서 최신 주보 정보 가져오기"""
    try:
        if os.path.exists('latest_bulletin.json'):
            with open('latest_bulletin.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        return None
    except Exception as e:
        print(f"파일에서 최신 주보 가져오기 실패: {e}")
        return None

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

def update_index_html(wr_id):
    """index.html 파일에서 wr_id 업데이트"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # wr_id 패턴 찾기 및 교체
        updated_content = re.sub(r'wr_id=\d+', f'wr_id={wr_id}', content)
        
        if content == updated_content:
            print("🔄 index.html에 변경할 내용이 없습니다.")
            return False # 변경사항 없음

        with open('index.html', 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✅ index.html 업데이트 완료: wr_id={wr_id}")
        return True
        
    except Exception as e:
        print(f"❌ index.html 업데이트 실패: {e}")
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
    
    # 파일에서 최신 주보 정보 가져오기
    file_latest = get_latest_bulletin_from_file()
    if file_latest:
        print(f"📋 파일 최신 주보: {file_latest['title']} (wr_id: {file_latest['wr_id']})")
    else:
        print("📋 파일에 주보 정보가 없습니다.")
    
    # 새로운 주보인지 확인
    if not file_latest or int(website_latest['wr_id']) > int(file_latest['wr_id']):
        print("🆕 새로운 주보가 발견되었습니다!")
        
        # index.html 업데이트
        if update_index_html(website_latest['wr_id']):
            # 최신 주보 정보 파일 업데이트
            update_latest_bulletin_file(website_latest)
            
            print("🎉 새로운 주보가 성공적으로 업데이트되었습니다!")
            print("📝 index.html이 최신 wr_id로 업데이트되었습니다.")
            return True
        else:
            print("❌ index.html 업데이트에 실패했습니다.")
            return False
    else:
        print("✅ 이미 최신 주보가 있습니다.")
        # 최신 주보 정보 파일 업데이트
        update_latest_bulletin_file(website_latest)
        return True

if __name__ == "__main__":
    check_and_update_latest_bulletin() 