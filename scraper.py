import cv2
import pytesseract
import re
import requests
from bs4 import BeautifulSoup, Tag
import os
from datetime import datetime
import sqlite3 # 데이터베이스 연결을 위해 추가
import numpy as np

# --- 영역별 OCR 설정 ---
# 페이지 번호가 아닌, 파일의 '순서'를 기준으로 OCR 영역을 정의합니다.
# 이 설정은 godswillseed.or.kr 게시판의 주보 파일 순서를 기준으로 합니다.
# 기준 해상도: 1748x2480
BASE_WIDTH = 1748
BASE_HEIGHT = 2480

# 각 파일 순서(인덱스 0부터 시작)에 해당하는 페이지의 종류
PAGE_ORDER = {
    0: "표지",
    1: "예배안내_페이지",
    2: "오늘의말씀_페이지",
    3: "교회소식_페이지",
    4: "기타" # 5번째 이미지는 보통 광고 등이므로 무시
}

# ROI 확장 유틸리티 (최소한으로 설정)
EXPAND = 2

def expand_roi(coords):
    x, y, w, h = coords
    return [max(0, x-EXPAND), max(0, y-EXPAND), w+2*EXPAND, h+2*EXPAND]

# 페이지 종류별 OCR 설정 (사용자가 제공한 정확한 좌표 기반)
PAGE_CONFIGS = {
    "표지": {
        "rois": [
            {"name": "통권", "coords": expand_roi([90, 100, 460, 70])},
            {"name": "날짜", "coords": expand_roi([900, 100, 740, 70])},
        ]
    },
    "예배안내_페이지": {
        "rois": [
            {"name": "예배안내", "coords": expand_roi([100, 70, 910, 2350])},
            {"name": "기도제목_통계", "coords": expand_roi([1070, 70, 650, 2350])},
        ]
    },
    "오늘의말씀_페이지": {
        "rois": [
             {"name": "오늘의 말씀", "coords": expand_roi([60, 90, 1650, 1700])},
             # {"name": "설교메모", "coords": expand_roi([60, 1790, 1650, 690])},  # 동적으로 처리하므로 주석 처리
        ]
    },
    "교회소식_페이지": {
        "rois": [
            {"name": "교회소식", "coords": expand_roi([70, 70, 1600, 2010])},
            {"name": "온라인헌금안내", "coords": expand_roi([70, 2100, 1600, 300])},
        ]
    }
}

def preprocess_for_ocr(image):
    """
    OCR 정확도를 높이기 위해 이미지 전처리를 수행합니다.
    """
    # 회색조 변환
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 노이즈 제거 (가우시안 블러)
    denoised = cv2.GaussianBlur(gray, (1, 1), 0)
    
    # 대비 향상 (CLAHE) - 더 강한 설정
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # 이진화 처리 (Otsu's method)
    _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 모폴로지 연산으로 텍스트 선명화
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    morph = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return morph

def ocr_crop_advanced(image, roi_config, scale_factors=(1.0, 1.0)):
    """
    고급 OCR 설정으로 텍스트 추출을 시도합니다.
    여러 설정을 시도하여 최적의 결과를 반환합니다.
    """
    x_scale, y_scale = scale_factors
    x, y, w, h = roi_config['coords']
    
    # ROI 좌표를 이미지 크기에 맞게 조정
    scaled_x = int(x * x_scale)
    scaled_y = int(y * y_scale)
    scaled_w = int(w * x_scale)
    scaled_h = int(h * y_scale)

    try:
        # 이미지를 numpy 배열로 변환
        roi = image[scaled_y:scaled_y+scaled_h, scaled_x:scaled_x+scaled_w]
        
        # 다양한 OCR 설정 시도
        ocr_configs = [
            '--psm 6 --oem 3 -c preserve_interword_spaces=1',  # 균등한 텍스트 블록
            '--psm 8 --oem 3 -c preserve_interword_spaces=1',  # 단일 단어
            '--psm 13 --oem 3 -c preserve_interword_spaces=1', # 원시 텍스트
            '--psm 3 --oem 3 -c preserve_interword_spaces=1',  # 자동 페이지 세그먼테이션
            '--psm 4 --oem 3 -c preserve_interword_spaces=1',  # 단일 컬럼 텍스트
        ]
        
        best_text = ""
        best_confidence = 0
        
        for config in ocr_configs:
            try:
                # 전처리된 이미지로 OCR
                preprocessed_roi = preprocess_for_ocr(roi)
                text = pytesseract.image_to_string(preprocessed_roi, lang='kor+eng', config=config).strip()
                
                # 신뢰도 확인 (가능한 경우)
                try:
                    data = pytesseract.image_to_data(preprocessed_roi, lang='kor+eng', config=config, output_type=pytesseract.Output.DICT)
                    confidence = sum(data['conf']) / len(data['conf']) if data['conf'] else 0
                except:
                    confidence = 50  # 기본값
                
                # 더 긴 텍스트와 높은 신뢰도를 우선
                if len(text) > len(best_text) and confidence > best_confidence:
                    best_text = text
                    best_confidence = confidence
                    
            except Exception as e:
                continue
        
        # 결과가 없으면 기본 설정으로 재시도
        if not best_text:
            preprocessed_roi = preprocess_for_ocr(roi)
            best_text = pytesseract.image_to_string(preprocessed_roi, lang='kor+eng', config='--psm 6').strip()
        
        return f"### {roi_config['name']}\n\n{best_text}"
        
    except Exception as e:
        print(f"영역({roi_config['name']}) OCR 실패: {e}")
        return f"### {roi_config['name']}\n\n(텍스트 추출 실패)"

def ocr_crop(image, roi_config, scale_factors=(1.0, 1.0)):
    """
    이미지와 ROI 설정에 따라 특정 영역들에서 OCR 수행 (크기 동적 조정)
    고급 OCR 함수를 사용합니다.
    """
    return ocr_crop_advanced(image, roi_config, scale_factors)

def ocr_full_image(image_path):
    """
    이미지 전체에서 텍스트를 추출합니다.
    """
    try:
        text = pytesseract.image_to_string(image_path, lang='kor+eng')
        return text.strip()
    except Exception as e:
        print(f"OCR 처리 실패: {image_path} - {e}")
        return ""

def extract_bulletin_images_from_html(html_content):
    """
    HTML에서 주보 이미지 URL들을 추출
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 주보 이미지들이 있는 div 찾기
    img_div = soup.find("div", id="bo_v_img")
    if not isinstance(img_div, Tag):
        print("주보 이미지 div를 찾을 수 없습니다.")
        return []
    
    # 이미지 URL들 추출
    image_urls = []
    for img_tag in img_div.find_all("img"):
        if isinstance(img_tag, Tag):
            img_url = img_tag.get("src")
            if isinstance(img_url, str):
                if not img_url.startswith("http"):
                    img_url = "https://www.godswillseed.or.kr" + img_url
                image_urls.append(img_url)
    
    return image_urls

def extract_bulletin_metadata_from_html(html_content):
    """
    HTML에서 주보 메타데이터 추출 (제목, 날짜, 작성자 등)
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    metadata = {}
    
    # 제목 추출
    title_tag = soup.find("span", class_="bo_v_tit")
    if title_tag:
        metadata['title'] = title_tag.get_text(strip=True)
    
    # 작성자, 작성일, 조회수 추출
    user_info = soup.find("div", class_="bo_v_user")
    if isinstance(user_info, Tag):
        spans = user_info.find_all("span")
        for span in spans:
            text = span.get_text(strip=True)
            if "글쓴이" in text:
                metadata['author'] = text.replace("글쓴이", "").strip()
            elif "작성일" in text:
                date_str = text.replace("작성일", "").strip()
                metadata['date'] = date_str
            elif "조회수" in text:
                views_str = text.replace("조회수", "").strip()
                metadata['views'] = views_str
    
    return metadata

def download_bulletin_images(page_url, save_dir="downloads"):
    """
    주보 페이지에서 이미지들을 다운로드
    """
    try:
        print(f"페이지 다운로드 중: {page_url}")
        res = requests.get(page_url)
        res.raise_for_status()
        
        # HTML에서 주보 이미지 URL들 추출
        image_urls = extract_bulletin_images_from_html(res.text)
        
        if not image_urls:
            print("주보 이미지를 찾을 수 없습니다.")
            return [], {}
        
        print(f"발견된 이미지 수: {len(image_urls)}")
        
        # 메타데이터 추출
        metadata = extract_bulletin_metadata_from_html(res.text)
        print(f"메타데이터: {metadata}")
        
        # 이미지 다운로드
        img_paths = []
        os.makedirs(save_dir, exist_ok=True)
        
        for i, img_url in enumerate(image_urls):
            try:
                print(f"이미지 다운로드 중 ({i+1}/{len(image_urls)}): {img_url}")
                img_response = requests.get(img_url)
                img_response.raise_for_status()
                
                # 파일명 생성 (날짜_페이지번호.확장자)
                date_str = metadata.get('date', datetime.now().strftime('%Y%m%d'))
                date_str = date_str.replace('.', '').replace('-', '')
                
                # URL에서 확장자 추출 시 쿼리 스트링 등 제거
                extension = os.path.splitext(img_url.split('?')[0])[-1]
                if not extension: # 확장자가 없는 경우 (e.g. cdn)
                    content_type = img_response.headers.get('content-type')
                    if content_type and 'jpeg' in content_type:
                        extension = '.jpeg'
                    else:
                        extension = '.jpg' # 기본값
                        
                filename = f"{date_str}_page_{i+1:02d}{extension}"
                
                img_path = os.path.join(save_dir, filename)
                
                with open(img_path, "wb") as f:
                    f.write(img_response.content)
                
                img_paths.append(img_path)
                print(f"다운로드 완료: {img_path}")
                
            except Exception as e:
                print(f"이미지 다운로드 실패: {img_url} - {e}")
        
        return img_paths, metadata
        
    except Exception as e:
        print(f"페이지 처리 실패: {page_url} - {e}")
        return [], {}

def extract_bulletin_info(image_path):
    """
    이미지에서 주보 정보 추출 (OCR)
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"이미지를 읽을 수 없습니다: {image_path}")
            return None, None

        # 좌측 상단 (권, 호, 통권) - 실제 이미지에서 좌표 측정 필요
        x1, y1, w1, h1 = 30, 40, 300, 50  # 예시 좌표
        roi1 = img[y1:y1+h1, x1:x1+w1]
        text1 = pytesseract.image_to_string(roi1, lang='kor+eng', config='--psm 7')

        # 우측 상단 (년, 월, 일) - 실제 이미지에서 좌표 측정 필요
        x2, y2, w2, h2 = 400, 40, 350, 50  # 예시 좌표
        roi2 = img[y2:y2+h2, x2:x2+w2]
        text2 = pytesseract.image_to_string(roi2, lang='kor+eng', config='--psm 7')

        return text1.strip(), text2.strip()
    except Exception as e:
        print(f"OCR 처리 실패: {image_path} - {e}")
        return None, None

def parse_multiple_bible_references(text):
    """
    OCR로 추출한 문자열에서 복수의 책, 장, 절 구절을 모두 파싱
    예: '마태복음 7:13-14, 시편 23:1-3' → [ ('마태복음', 7, 13, 14), ('시편', 23, 1, 3) ]
    """
    pattern = r'([가-힣]+)\s*(\d+):(\d+)(?:-(\d+))?'
    matches = re.findall(pattern, text)
    refs = []
    for m in matches:
        book = m[0]
        chapter = int(m[1])
        verse_start = int(m[2])
        verse_end = int(m[3]) if m[3] else verse_start
        refs.append({'book': book, 'chapter': chapter, 'verse_start': verse_start, 'verse_end': verse_end})
    return refs

def get_bskorea_bible_text_gae(book, chapter, verse_start, verse_end):
    # 이 함수는 예시이며, 실제 구현이 필요합니다.
    return f"{book} {chapter}:{verse_start}-{verse_end}의 성경 본문"

def get_bible_text_from_ocr_ref(ocr_text):
    return get_bskorea_bible_text_gae(ocr_text, 0, 0, 0) # 임시

def find_text_y_coordinate(image, text_to_find, search_roi_coords, scale_factors):
    """
    주어진 이미지와 ROI 내에서 특정 텍스트를 찾아 상단 y좌표를 반환합니다.
    (스케일링 적용됨)
    """
    x_scale, y_scale = scale_factors
    x, y, w, h = search_roi_coords
    
    # ROI 좌표를 이미지 크기에 맞게 조정
    scaled_x = int(x * x_scale)
    scaled_y = int(y * y_scale)
    scaled_w = int(w * x_scale)
    scaled_h = int(h * y_scale)

    try:
        search_area = image[scaled_y:scaled_y+scaled_h, scaled_x:scaled_x+scaled_w]
        preprocessed_roi = preprocess_for_ocr(search_area)
        
        details = pytesseract.image_to_data(preprocessed_roi, output_type=pytesseract.Output.DICT, lang='kor', config='--psm 3')
        
        full_text = "".join(details['text'])
        if text_to_find in full_text.replace(" ", "").replace("■",""):
             for i, text in enumerate(details['text']):
                if text_to_find in text:
                    return scaled_y + details['top'][i]

    except Exception as e:
        print(f"'{text_to_find}' 텍스트 위치 찾기 실패: {e}")
    
    return None

def find_sermon_memo_y(image, base_roi_coords, scale_factors):
    """
    '설교메모' 텍스트를 찾아 y좌표를 반환. 동적 ROI 계산에 사용.
    """
    x_scale, y_scale = scale_factors
    x, y, w, h = base_roi_coords

    # ROI 좌표를 이미지 크기에 맞게 조정
    scaled_x = int(x * x_scale)
    scaled_y = int(y * y_scale)
    scaled_w = int(w * x_scale)
    scaled_h = int(h * y_scale)
    
    try:
        roi = image[scaled_y:scaled_y+scaled_h, scaled_x:scaled_x+scaled_w]
        
        # '설교메모' 텍스트 위치 찾기
        # Tesseract의 oem 3, psm 3 조합이 전체 페이지 분석에 적합
        details = pytesseract.image_to_data(preprocess_for_ocr(roi), output_type=pytesseract.Output.DICT, lang='kor', config='--oem 3 --psm 3')
        
        for i, text in enumerate(details['text']):
            if '설교' in text or '메모' in text:
                # '설교메모' 텍스트의 y좌표 + 높이를 반환 (ROI 내 상대 좌표이므로 절대 좌표로 변환)
                text_y = details['top'][i]
                text_h = details['height'][i]
                return scaled_y + text_y + text_h # '설교메모' 텍스트 바로 아래 y좌표
    except Exception as e:
        print(f"'설교메모' 위치 찾기 실패: {e}")

    return None

def find_sermon_memo_start_dynamic(image, scale_factors):
    """
    3페이지에서 '설교메모' 텍스트의 시작 위치를 동적으로 찾습니다.
    오늘의 말씀 영역을 먼저 처리하고, 그 결과에 따라 설교메모 시작 위치를 결정합니다.
    """
    x_scale, y_scale = scale_factors
    
    # 오늘의 말씀 영역의 좌표 (고정)
    sermon_x, sermon_y, sermon_w, sermon_h = [60, 90, 1650, 1700]
    
    # 스케일링 적용
    scaled_sermon_x = int(sermon_x * x_scale)
    scaled_sermon_y = int(sermon_y * y_scale)
    scaled_sermon_w = int(sermon_w * x_scale)
    scaled_sermon_h = int(sermon_h * y_scale)
    
    try:
        # 오늘의 말씀 영역에서 텍스트 분석
        sermon_roi = image[scaled_sermon_y:scaled_sermon_y+scaled_sermon_h, scaled_sermon_x:scaled_sermon_x+scaled_sermon_w]
        preprocessed_sermon = preprocess_for_ocr(sermon_roi)
        
        # 고급 OCR 설정으로 텍스트 위치 정보 추출
        details = pytesseract.image_to_data(preprocessed_sermon, output_type=pytesseract.Output.DICT, lang='kor', config='--oem 3 --psm 3')
        
        # 텍스트가 있는 마지막 y좌표 찾기
        last_text_y = scaled_sermon_y
        for i, text in enumerate(details['text']):
            if text.strip():  # 빈 텍스트가 아닌 경우
                text_y = details['top'][i]
                text_h = details['height'][i]
                current_text_end = scaled_sermon_y + text_y + text_h
                last_text_y = max(last_text_y, current_text_end)
        
        # 오늘의 말씀 영역에서 텍스트가 끝나는 지점 + 여백(20px)을 설교메모 시작점으로 설정
        sermon_memo_start = last_text_y + int(20 * y_scale)
        
        # 페이지 하단을 넘지 않도록 제한
        page_height = image.shape[0]
        sermon_memo_start = min(sermon_memo_start, page_height - int(100 * y_scale))
        
        return sermon_memo_start
        
    except Exception as e:
        print(f"설교메모 시작 위치 찾기 실패: {e}")
        # 실패 시 기본값 반환 (오늘의 말씀 영역 바로 아래)
        return scaled_sermon_y + scaled_sermon_h + int(20 * y_scale)

def ocr_crop_dynamic(image, roi_config, scale_factors, dynamic_end_y=None):
    x_scale, y_scale = scale_factors
    x, y, w, h = roi_config['coords']

    # ROI 좌표를 이미지 크기에 맞게 조정
    scaled_x = int(x * x_scale)
    scaled_y = int(y * y_scale)
    scaled_w = int(w * x_scale)
    
    if dynamic_end_y is not None:
        # dynamic_end_y는 이미 스케일된 이미지 기준의 좌표.
        # 따라서 추가 스케일링 불필요. 단, ROI의 시작 y좌표보다는 커야 함.
        scaled_h = max(0, dynamic_end_y - scaled_y)
    else:
        # dynamic_end_y를 못찾으면 원래 h값을 스케일해서 사용
        scaled_h = int(h * y_scale)

    # ocr_crop은 좌표를 다시 스케일링 하므로, 이미 계산된 좌표를 넘길때는 스케일 팩터를 1로 준다.
    return ocr_crop(image, {'name': roi_config['name'], 'coords': [scaled_x, scaled_y, scaled_w, scaled_h]}, scale_factors=(1.0, 1.0))

def process_bulletin_urls(urls):
    """
    주어진 URL 목록을 순회하며 각 주보를 처리
    """
    conn = sqlite3.connect('weekly_posts.db')
    cursor = conn.cursor()

    for url in urls:
        print(f"\n=== 주보 처리 중: {url} ===")
        wr_id = url.split('wr_id=')[-1]

        # 데이터베이스에서 해당 wr_id의 ocr_data를 강제로 다시 생성하려면 아래 주석을 해제하세요.
        cursor.execute("UPDATE weekly_posts SET ocr_data = NULL WHERE wr_id=?", (wr_id,))
        conn.commit()

        # 데이터베이스에서 해당 wr_id의 ocr_data가 이미 있는지 확인
        cursor.execute("SELECT ocr_data FROM weekly_posts WHERE wr_id=?", (wr_id,))
        result = cursor.fetchone()

        # 이미 데이터가 있고, 비어있지 않다면 건너뛰기
        if result and result[0]:
            print(f"wr_id={wr_id}는 이미 처리되었습니다. 건너뜁니다.")
            continue

        downloaded_files, metadata = download_bulletin_images(url)
        
        if not downloaded_files:
            continue

        ocr_results = []
        print(f"\n--- 고정된 순서에 따라 페이지별 OCR 처리 시작 (총 {len(downloaded_files)}페이지) ---\n")

        for i, img_path in enumerate(downloaded_files):
            print(f"[파일 {i+1}] 처리 중: {img_path}")
            page_type = PAGE_ORDER.get(i, "기타")
            
            if page_type == "기타":
                print(f"  > '기타' 페이지 유형이므로 건너뜁니다.")
                continue

            img = cv2.imread(img_path)
            if img is None:
                print(f"  > 이미지를 읽을 수 없습니다: {img_path}")
                continue

            actual_height, actual_width, _ = img.shape
            x_scale = actual_width / BASE_WIDTH
            y_scale = actual_height / BASE_HEIGHT
            scale_factors = (x_scale, y_scale)

            print(f"  > '{page_type}'으로 처리합니다.")

            if page_type in PAGE_CONFIGS:
                page_config = PAGE_CONFIGS[page_type]
                
                # 3페이지(오늘의말씀_페이지)의 경우 특별 처리
                if page_type == "오늘의말씀_페이지":
                    # 1. 먼저 "오늘의 말씀" 영역 처리
                    sermon_roi = page_config["rois"][0]  # 첫 번째 ROI는 "오늘의 말씀"
                    sermon_text = ocr_crop(img, sermon_roi, scale_factors)
                    ocr_results.append(sermon_text)
                    
                    # 2. 설교메모 시작 위치를 동적으로 찾기
                    sermon_memo_start_y = find_sermon_memo_start_dynamic(img, scale_factors)
                    
                    # 3. 동적으로 계산된 위치로 설교메모 영역 처리
                    if sermon_memo_start_y:
                        # 설교메모 영역의 좌표 계산 (x, y, width, height)
                        sermon_memo_x = int(60 * x_scale)  # x 좌표는 고정
                        sermon_memo_w = int(1650 * x_scale)  # 너비는 고정
                        sermon_memo_h = img.shape[0] - sermon_memo_start_y - int(20 * y_scale)  # 페이지 하단까지
                        
                        # 설교메모 영역이 너무 작으면 건너뛰기
                        if sermon_memo_h > int(50 * y_scale):
                            dynamic_roi = {
                                'name': '설교메모',
                                'coords': [sermon_memo_x, sermon_memo_start_y, sermon_memo_w, sermon_memo_h]
                            }
                            memo_text = ocr_crop(img, dynamic_roi, scale_factors=(1.0, 1.0))
                            ocr_results.append(memo_text)
                        else:
                            print(f"  > 설교메모 영역이 너무 작아서 건너뜁니다. (높이: {sermon_memo_h}px)")
                    else:
                        print(f"  > 설교메모 시작 위치를 찾을 수 없어서 건너뜁니다.")
                
                else:
                    # 다른 페이지들은 기존 방식대로 고정 ROI 처리
                    for roi_config in page_config["rois"]:
                        text = ocr_crop(img, roi_config, scale_factors)
                        ocr_results.append(text)

        # 데이터베이스에 OCR 결과 저장
        final_ocr_text = "\n\n---\n\n".join(ocr_results)
        try:
            cursor.execute(
                "UPDATE weekly_posts SET ocr_data = ? WHERE wr_id = ?",
                (final_ocr_text, wr_id)
            )
            conn.commit()
            print(f"\nDB 업데이트 완료: wr_id={wr_id}의 OCR 데이터가 저장되었습니다.")
        except Exception as e:
            print(f"DB 업데이트 실패: wr_id={wr_id} - {e}")
            conn.rollback()
    
    conn.close()


def get_latest_bulletin_urls(base_url="https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly"):
    """
    교회 주보 게시판에서 최근 3개의 주보 URL을 가져옴
    """
    try:
        res = requests.get(base_url)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        
        post_links = []
        # '공지'가 아닌 일반 게시물을 찾습니다.
        for post in soup.select("tbody tr:not(.bo_notice)"):
            link_tag = post.select_one("td.td_subject a")
            if link_tag and 'href' in link_tag.attrs:
                post_links.append(link_tag['href'])
                if len(post_links) >= 3:
                    break
        return post_links
    except Exception as e:
        print(f"최신 주보 URL을 가져오는데 실패했습니다: {e}")
        return []

if __name__ == "__main__":
    # 최근 3개 주보 URL 가져오기
    latest_urls = get_latest_bulletin_urls()
    
    if latest_urls:
        process_bulletin_urls(latest_urls)
        print("\n=== 모든 주보 처리 완료 ===")
    else:
        print("처리할 주보가 없습니다.")