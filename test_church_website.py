import requests
from bs4 import BeautifulSoup

def test_church_website():
    """교회 웹사이트 접속 테스트"""
    
    # 다양한 User-Agent 시도
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        'Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
    ]
    
    url = "https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly"
    
    for i, user_agent in enumerate(user_agents):
        print(f"\n🔍 테스트 {i+1}: {user_agent[:50]}...")
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            print(f"  상태 코드: {response.status_code}")
            print(f"  응답 크기: {len(response.text)} bytes")
            
            # 응답 내용 확인
            if "자동등록방지" in response.text or "보안절차" in response.text:
                print(f"  ❌ 보안절차 감지됨")
                print(f"  응답 내용 일부: {response.text[:200]}...")
            else:
                print(f"  ✅ 정상 접속됨")
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 주보 링크 찾기
                links = soup.find_all('a', href=True)
                weekly_links = [link for link in links if 'wr_id=' in link.get('href', '')]
                
                if weekly_links:
                    print(f"  📋 주보 링크 {len(weekly_links)}개 발견")
                    for j, link in enumerate(weekly_links[:3]):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        print(f"    {j+1}. {text} -> {href}")
                    break
                else:
                    print(f"  ⚠️  주보 링크를 찾을 수 없음")
                    
        except Exception as e:
            print(f"  ❌ 오류: {e}")

if __name__ == "__main__":
    test_church_website() 