#!/usr/bin/env python3
"""
정기적으로 최신 주보를 확인하고 자동으로 업데이트하는 스크립트
"""

import requests
from bs4 import BeautifulSoup, Tag
import re
from datetime import datetime
import subprocess
import os

def get_latest_bulletin_id():
    """교회 웹사이트에서 최신 주보 wr_id 가져오기"""
    try:
        list_url = "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(list_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        latest_link_tag = soup.find('a', href=lambda href: isinstance(href, str) and 'wr_id=' in href and 'weekly' in href)
        
        if not isinstance(latest_link_tag, Tag):
            print("최신 주보 링크를 찾을 수 없습니다.")
            return None

        post_url = str(latest_link_tag.get('href', ''))
        wr_id_match = re.search(r'wr_id=(\d+)', post_url)
        
        if wr_id_match:
            return wr_id_match.group(1)
        
        return None
        
    except Exception as e:
        print(f"최신 주보 ID 가져오기 실패: {e}")
        return None

def update_index_html(wr_id):
    """index.html 파일에서 wr_id 업데이트"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
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

def git_commit_and_push():
    """변경사항을 Git에 커밋하고 푸시"""
    try:
        subprocess.run(['git', 'config', '--local', 'user.email', 'action@github.com'], check=True)
        subprocess.run(['git', 'config', '--local', 'user.name', 'GitHub Action'], check=True)
        
        subprocess.run(['git', 'add', 'index.html'], check=True)
        
        commit_message = f'Auto update latest bulletin wr_id - {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        subprocess.run(['git', 'push'], check=True)
        
        print("✅ Git 커밋 및 푸시 완료")
        return True
        
    except Exception as e:
        print(f"❌ Git 작업 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print(f"🔄 최신 주보 확인 시작: {datetime.now()}")
    
    latest_wr_id = get_latest_bulletin_id()
    
    if latest_wr_id:
        print(f"📋 최신 주보 발견: wr_id={latest_wr_id}")
        
        if update_index_html(latest_wr_id):
            if git_commit_and_push():
                print("🎉 자동 업데이트 완료!")
            else:
                print("⚠️ Git 푸시 실패")
    else:
        print("❌ 최신 주보 정보를 가져올 수 없습니다")

if __name__ == "__main__":
    main() 