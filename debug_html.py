import requests
from bs4 import BeautifulSoup
import urllib3

# SSL 경고 비활성화
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def debug_post(wr_id):
    base_url = "https://www.godswillseed.or.kr/bbs/board.php"
    params = {
        'bo_table': 'weekly',
        'wr_id': wr_id
    }
    
    response = requests.get(base_url, params=params, verify=False)
    response.raise_for_status()
    
    # 전체 HTML 저장
    with open(f'post_{wr_id}_full.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 주요 부분 출력
    print("\n=== 제목 관련 요소 ===")
    title_elem = soup.find('h2', id='bo_v_title')
    if title_elem:
        print(title_elem.prettify())
    
    print("\n=== 내용 관련 요소 ===")
    content = soup.find('div', id='bo_v_con')
    if content:
        print(content.prettify())
    
    print("\n=== 이미지 태그들 ===")
    images = soup.find_all('img')
    for img in images:
        print(img.prettify())

if __name__ == "__main__":
    debug_post(731) 