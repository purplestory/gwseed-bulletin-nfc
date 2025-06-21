import requests
from bs4 import BeautifulSoup
import re

def debug_latest_bulletin():
    """교회 주보 게시판에서 최신 주보 URL을 디버깅"""
    try:
        # 교회 주보 게시판 URL
        base_url = "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly"
        
        print(f"🔍 접속 URL: {base_url}")
        
        # 페이지 요청
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(base_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"✅ 응답 상태: {response.status_code}")
        print(f"📄 응답 크기: {len(response.text)} bytes")
        
        # HTML 파싱
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 모든 링크 찾기
        print("\n🔗 모든 링크:")
        all_links = soup.find_all('a', href=True)
        for i, link in enumerate(all_links[:10]):  # 처음 10개만 출력
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"  {i+1}. {text} -> {href}")
        
        # 테이블 구조 확인
        print("\n📋 테이블 구조:")
        tables = soup.find_all('table')
        for i, table in enumerate(tables):
            print(f"  테이블 {i+1}: {len(table.find_all('tr'))} 행")
        
        # tbody 확인
        tbody = soup.find('tbody')
        if tbody:
            print(f"\n📝 tbody 내용:")
            rows = tbody.find_all('tr')
            for i, row in enumerate(rows[:5]):  # 처음 5개 행만
                cells = row.find_all('td')
                print(f"  행 {i+1}: {len(cells)} 셀")
                for j, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    links = cell.find_all('a')
                    print(f"    셀 {j+1}: '{text}' (링크 {len(links)}개)")
        
        # 최신 주보 링크 찾기 (다양한 방법 시도)
        print("\n🎯 최신 주보 링크 찾기:")
        
        # 방법 1: td_subject 클래스
        subject_links = soup.select("td.td_subject a")
        print(f"  방법 1 (td_subject): {len(subject_links)}개 링크")
        if subject_links:
            for i, link in enumerate(subject_links[:3]):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"    {i+1}. {text} -> {href}")
        
        # 방법 2: 일반 게시물 (공지사항 제외)
        post_links = soup.select("tbody tr:not(.bo_notice) td.td_subject a")
        print(f"  방법 2 (일반게시물): {len(post_links)}개 링크")
        if post_links:
            for i, link in enumerate(post_links[:3]):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"    {i+1}. {text} -> {href}")
        
        # 방법 3: 모든 링크에서 주보 관련 찾기
        weekly_links = []
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if 'wr_id=' in href and ('주보' in text or 'weekly' in href):
                weekly_links.append((text, href))
        
        print(f"  방법 3 (주보키워드): {len(weekly_links)}개 링크")
        for i, (text, href) in enumerate(weekly_links[:3]):
            print(f"    {i+1}. {text} -> {href}")
        
        # 방법 4: wr_id 패턴 찾기
        wr_id_links = []
        for link in all_links:
            href = link.get('href', '')
            if 'wr_id=' in href:
                wr_id_links.append((link.get_text(strip=True), href))
        
        print(f"  방법 4 (wr_id패턴): {len(wr_id_links)}개 링크")
        for i, (text, href) in enumerate(wr_id_links[:3]):
            print(f"    {i+1}. {text} -> {href}")
        
        return None
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        return None

if __name__ == "__main__":
    debug_latest_bulletin() 