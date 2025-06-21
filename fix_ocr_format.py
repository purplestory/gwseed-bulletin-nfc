import sqlite3

def fix_ocr_format():
    """기존 OCR 데이터의 이스케이프된 줄바꿈을 실제 줄바꿈으로 변환"""
    conn = sqlite3.connect('weekly_posts.db')
    cursor = conn.cursor()
    
    # 모든 OCR 데이터 가져오기
    cursor.execute("SELECT id, ocr_data FROM weekly_posts WHERE ocr_data IS NOT NULL")
    rows = cursor.fetchall()
    
    fixed_count = 0
    for row in rows:
        post_id, ocr_data = row
        if ocr_data and '\\n\\n' in ocr_data:
            # 이스케이프된 줄바꿈을 실제 줄바꿈으로 변환
            fixed_ocr_data = ocr_data.replace('\\n\\n', '\n\n').replace('\\n', '\n')
            
            # 데이터베이스 업데이트
            cursor.execute("UPDATE weekly_posts SET ocr_data = ? WHERE id = ?", (fixed_ocr_data, post_id))
            fixed_count += 1
            print(f"수정됨: post_id={post_id}")
    
    conn.commit()
    conn.close()
    
    print(f"\n총 {fixed_count}개의 OCR 데이터가 수정되었습니다.")

if __name__ == "__main__":
    fix_ocr_format() 