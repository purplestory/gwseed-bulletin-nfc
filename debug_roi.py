import cv2
import os
from scraper import (PAGE_ORDER, PAGE_CONFIGS, BASE_WIDTH, BASE_HEIGHT, EXPAND)

# 디버깅할 주보의 이미지 파일 경로 (최신 주보 기준)
IMAGE_FILES = [
    'downloads/20250614_page_01.jpeg',
    'downloads/20250614_page_02.jpeg',
    'downloads/20250614_page_03.jpeg',
    'downloads/20250614_page_04.jpeg',
]

# 결과물을 저장할 디렉토리
OUTPUT_DIR = 'debug_output'
os.makedirs(OUTPUT_DIR, exist_ok=True)


def draw_roi_on_image():
    """
    이미지 위에 설정된 모든 고정 ROI 영역을 사각형으로 그립니다.
    """
    print("ROI 디버깅 이미지 생성을 시작합니다...")
    
    for idx, img_path in enumerate(IMAGE_FILES):
        if not os.path.exists(img_path):
            print(f"이미지 파일을 찾을 수 없습니다: {img_path}")
            continue
            
        image = cv2.imread(img_path)
        if image is None:
            print(f"이미지를 읽을 수 없습니다: {img_path}")
            continue
            
        actual_height, actual_width, _ = image.shape
        x_scale = actual_width / BASE_WIDTH
        y_scale = actual_height / BASE_HEIGHT
        
        print(f"\n[파일 {idx+1}] {os.path.basename(img_path)}")
        
        page_type = PAGE_ORDER.get(idx, "기타")
        print(f"  페이지 유형: {page_type}")
        
        if page_type in PAGE_CONFIGS:
            page_config = PAGE_CONFIGS[page_type]
            
            for roi_config in page_config["rois"]:
                name = roi_config['name']
                x, y, w, h = roi_config['coords']
                
                scaled_x = int(x * x_scale)
                scaled_y = int(y * y_scale)
                scaled_w = int(w * x_scale)
                scaled_h = int(h * y_scale)
                
                # 영역별 색상 구분
                color = (0, 0, 255) # 기본값: 빨간색
                if "좌측" in name:
                    color = (0, 0, 255) # 빨간색
                elif "우측" in name:
                    color = (255, 0, 0) # 파란색
                elif "말씀" in name or "소식" in name:
                     color = (0, 165, 255) # 주황색
                else:
                    color = (0, 255, 0) # 초록색
                
                cv2.rectangle(image, (scaled_x, scaled_y), (scaled_x + scaled_w, scaled_y + scaled_h), color, 3)
                cv2.putText(image, f"{name}", (scaled_x, scaled_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        output_filename = f"debug_{os.path.basename(img_path)}"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        cv2.imwrite(output_path, image)
        print(f"  디버깅 이미지 저장 완료: {output_path}")

def show_roi_summary():
    """
    현재 설정된 모든 ROI 좌표를 요약하여 출력합니다.
    """
    print("\n=== 현재 설정된 ROI 좌표 요약 ===")
    print(f"기준 해상도: {BASE_WIDTH}x{BASE_HEIGHT}")
    print(f"ROI 확장: {EXPAND}px")
    
    for page_type, config in PAGE_CONFIGS.items():
        print(f"\n[{page_type}]")
        for roi in config['rois']:
            x, y, w, h = roi['coords']
            print(f"  {roi['name']}: ({x}, {y}, {w}, {h})")

if __name__ == '__main__':
    show_roi_summary()
    draw_roi_on_image()
    print("\n=== 작업 완료 ===")
    print("'debug_output' 폴더에서 결과 이미지를 확인하세요.")
    print("모든 페이지의 좌표가 정확하게 표시되었는지 최종 확인해주세요.") 