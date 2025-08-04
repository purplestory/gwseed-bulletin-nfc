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
    
    # 여러 User-Agent 시도
    user_agents = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
        'curl/7.68.0',  # GitHub Actions 환경에서 사용 가능한 curl
        # GitHub Actions 환경용 추가 User-Agent
        'Mozilla/5.0 (Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # 추가 실제 브라우저 User-Agent
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
    ]
    
    for i, user_agent in enumerate(user_agents, 1):
        try:
            print(f"🔄 시도 {i}/{len(user_agents)}: {user_agent[:50]}...")
            
            url = "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly"
            
            # 더 실제적인 브라우저 헤더 설정
            headers = {
                'User-Agent': user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
                # GitHub Actions 환경용 추가 헤더
                'X-Forwarded-For': '127.0.0.1',
                'X-Real-IP': '127.0.0.1',
                'X-Requested-With': 'XMLHttpRequest',
                # 추가 봇 차단 우회 헤더
                'Referer': 'https://www.godswillseed.or.kr/',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-User': '?1'
            }
            
            # 세션 사용으로 쿠키 유지
            session = requests.Session()
            session.headers.update(headers)
            
            # 먼저 메인 페이지에 접속 (봇 감지 방지)
            print(f"🔄 메인 페이지 접속 중...")
            main_response = session.get("https://www.godswillseed.or.kr/", timeout=15)
            main_response.raise_for_status()
            
            # 잠시 대기 (봇 감지 방지)
            import time
            time.sleep(2)
            
            # JavaScript 실행을 시뮬레이션하기 위해 추가 요청
            print(f"🔄 JavaScript 환경 시뮬레이션...")
            js_response = session.get("https://www.godswillseed.or.kr/cupid.js", timeout=10)
            time.sleep(1)
            
            # 주보 페이지 접속
            print(f"🔄 주보 페이지 접속 중...")
            response = session.get(url, timeout=15)
            response.raise_for_status()
            
            # 디버그: 응답 내용 확인
            print(f"📄 응답 상태 코드: {response.status_code}")
            print(f"📄 응답 헤더: {dict(response.headers)}")
            print(f"📄 응답 내용 길이: {len(response.text)} 문자")
            
            # 응답 내용의 일부를 출력 (디버그용)
            content_preview = response.text[:500]
            print(f"📄 응답 내용 미리보기: {content_preview}")
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 최신 주보 링크 찾기 (여러 방법 시도)
            latest_post = None
            
            # 방법 1: 단순한 텍스트에서 wr_id 패턴 찾기 (가장 먼저 시도)
            text_content = response.text
            wr_id_matches = re.findall(r'wr_id=(\d+)', text_content)
            if wr_id_matches:
                latest_wr_id = max(wr_id_matches, key=int)
                latest_url = f"https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly&wr_id={latest_wr_id}"
                
                latest_post = {
                    'url': latest_url,
                    'wr_id': latest_wr_id,
                    'title': f"주보 {latest_wr_id}",
                    'timestamp': datetime.now().isoformat()
                }
                print(f"✅ User-Agent {i}로 성공 (텍스트 검색): wr_id={latest_wr_id}")
                return latest_post
            
            # 방법 2: 기존 방법 (tbody tr:not(.bo_notice))
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
                        print(f"✅ User-Agent {i}로 성공: wr_id={wr_id}")
                        return latest_post
            
            # 방법 3: 모든 링크에서 wr_id 찾기
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = str(link['href'])
                if 'wr_id=' in href and 'weekly' in href:
                    if not href.startswith('http'):
                        href = "https://www.godswillseed.or.kr" + href
                    
                    # wr_id 추출
                    wr_id_match = re.search(r'wr_id=(\d+)', href)
                    wr_id = wr_id_match.group(1) if wr_id_match else None
                    
                    # 제목 추출
                    title = link.get_text(strip=True)
                    
                    latest_post = {
                        'url': href,
                        'wr_id': wr_id,
                        'title': title,
                        'timestamp': datetime.now().isoformat()
                    }
                    print(f"✅ User-Agent {i}로 성공 (방법 2): wr_id={wr_id}")
                    return latest_post
            
            print(f"❌ User-Agent {i}로 실패: 주보 링크를 찾을 수 없습니다.")
            
        except Exception as e:
            print(f"❌ User-Agent {i}로 실패: {e}")
            continue
    
    print("❌ 모든 User-Agent 시도가 실패했습니다.")
    
    # 웹사이트 접근이 완전히 실패한 경우
    print("❌ 교회 웹사이트에 접근할 수 없습니다. 수동 확인이 필요합니다.")
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
        
        # wr_id 패턴 찾기 및 교체 (여러 곳에서 교체)
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