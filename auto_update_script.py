#!/usr/bin/env python3
"""
정기적으로 최신 주보를 확인하고 자동으로 업데이트하는 스크립트
매주 일요일 오전 9시에 실행되도록 cron job 설정
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import os
from datetime import datetime
import subprocess

def get_latest_bulletin():
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

def update_index_html(wr_id):
    """index.html 파일에서 wr_id 업데이트"""
    try:
        # index.html 파일 읽기
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # wr_id 업데이트
        old_pattern = r'wr_id=\d+'
        new_url = f'wr_id={wr_id}'
        updated_content = re.sub(old_pattern, new_url, content)
        
        # 파일에 저장
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
        # Git 명령어 실행
        subprocess.run(['git', 'add', 'index.html'], check=True)
        subprocess.run(['git', 'commit', '-m', f'Auto update latest bulletin - {datetime.now().strftime("%Y-%m-%d %H:%M")}'], check=True)
        subprocess.run(['git', 'push'], check=True)
        
        print("✅ Git 커밋 및 푸시 완료")
        return True
        
    except Exception as e:
        print(f"❌ Git 작업 실패: {e}")
        return False

def main():
    """메인 실행 함수"""
    print(f"🔄 최신 주보 확인 시작: {datetime.now()}")
    
    # 최신 주보 정보 가져오기
    latest_info = get_latest_bulletin()
    
    if latest_info:
        print(f"📋 최신 주보 발견: wr_id={latest_info['wr_id']}")
        
        # index.html 업데이트
        if update_index_html(latest_info['wr_id']):
            # Git 커밋 및 푸시
            if git_commit_and_push():
                print("🎉 자동 업데이트 완료!")
            else:
                print("⚠️ Git 푸시 실패")
        else:
            print("❌ 파일 업데이트 실패")
    else:
        print("❌ 최신 주보 정보를 가져올 수 없습니다")

if __name__ == "__main__":
    main() 