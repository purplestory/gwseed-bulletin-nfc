from flask import Flask, render_template, redirect, url_for, send_from_directory, request, flash, session
import sqlite3
from datetime import datetime
import os
from PIL import Image
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 세션을 위한 시크릿 키

# 관리자 비밀번호 (실제 운영시에는 환경변수나 설정 파일에서 관리)
ADMIN_PASSWORD = 'admin123'

def markdown_to_html(text):
    """간단한 마크다운을 HTML로 변환"""
    if not text:
        return ""
    
    # 헤더 변환 (###### -> <h6>, ##### -> <h5>, #### -> <h4>, ### -> <h3>, ## -> <h2>, # -> <h1>)
    text = re.sub(r'^###### (.+)$', r'<h6>\1</h6>', text, flags=re.MULTILINE)
    text = re.sub(r'^##### (.+)$', r'<h5>\1</h5>', text, flags=re.MULTILINE)
    text = re.sub(r'^#### (.+)$', r'<h4>\1</h4>', text, flags=re.MULTILINE)
    text = re.sub(r'^### (.+)$', r'<h3>\1</h3>', text, flags=re.MULTILINE)
    text = re.sub(r'^## (.+)$', r'<h2>\1</h2>', text, flags=re.MULTILINE)
    text = re.sub(r'^# (.+)$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
    
    # 볼드 처리 (**텍스트** -> <strong>텍스트</strong>)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'__(.+?)__', r'<strong>\1</strong>', text)
    
    # 줄바꿈 변환
    text = text.replace('\n', '<br>')
    
    return text

# 마크다운 필터를 Jinja2에 등록
app.jinja_env.filters['markdown'] = markdown_to_html

# downloads 폴더를 정적 파일로 서빙
@app.route('/downloads/<path:filename>')
def download_file(filename):
    return send_from_directory('downloads', filename)

def get_db_connection():
    conn = sqlite3.connect('weekly_posts.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_post_with_navigation(wr_id=None):
    conn = get_db_connection()
    
    # wr_id가 없으면 가장 최근 게시물 가져오기
    if wr_id is None:
        post = conn.execute('SELECT * FROM weekly_posts ORDER BY wr_id DESC LIMIT 1').fetchone()
        if not post:
            conn.close()
            return None, None, None
        wr_id = post['wr_id']
    else:
        post = conn.execute('SELECT * FROM weekly_posts WHERE wr_id = ?', (wr_id,)).fetchone()
    
    # 이전 게시물 (더 작은 wr_id)
    prev_post = conn.execute(
        'SELECT * FROM weekly_posts WHERE wr_id < ? ORDER BY wr_id DESC LIMIT 1',
        (wr_id,)
    ).fetchone()
    
    # 다음 게시물 (더 큰 wr_id)
    next_post = conn.execute(
        'SELECT * FROM weekly_posts WHERE wr_id > ? ORDER BY wr_id ASC LIMIT 1',
        (wr_id,)
    ).fetchone()
    
    conn.close()
    return post, prev_post, next_post

def get_all_posts():
    """모든 주보 목록 가져오기"""
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM weekly_posts ORDER BY wr_id DESC').fetchall()
    conn.close()
    return posts

def format_bulletin_date(date_str):
    """날짜 문자열을 한국어 형식으로 변환"""
    if not date_str:
        return None
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return f"{dt.year}년 {dt.month}월 {dt.day}일"
    except Exception:
        return date_str

def get_image_paths(post):
    """주보의 이미지 경로들을 리스트로 반환"""
    if not post or not post['image_paths']:
        return []
    
    image_paths = post['image_paths'].split(',')
    # downloads 폴더 경로 추가
    return [f"downloads/{path.strip()}" for path in image_paths if path.strip()]

@app.route('/')
def index():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM weekly_posts ORDER BY created_at DESC LIMIT 1').fetchall()
    conn.close()
    
    if posts:
        return redirect(url_for('post', post_id=posts[0]['id']))
    return "주보가 없습니다."

@app.route('/post/<int:post_id>')
def post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM weekly_posts WHERE id = ?', (post_id,)).fetchone()
    
    prev_post = None
    next_post = None
    
    if post:
        # 이전 게시물 (더 작은 wr_id)
        prev_post = conn.execute(
            'SELECT * FROM weekly_posts WHERE wr_id < ? ORDER BY wr_id DESC LIMIT 1',
            (post['wr_id'],)
        ).fetchone()
        
        # 다음 게시물 (더 큰 wr_id)
        next_post = conn.execute(
            'SELECT * FROM weekly_posts WHERE wr_id > ? ORDER BY wr_id ASC LIMIT 1',
            (post['wr_id'],)
        ).fetchone()

    if post is None:
        conn.close()
        return "주보를 찾을 수 없습니다.", 404
    
    # 이미지 파일 정보 (이름, 너비, 높이) 생성
    image_files_with_dims = []
    if post['image_paths']:
        image_paths = post['image_paths'].split(',')
        for path in image_paths:
            filename = path.strip()
            if filename:
                try:
                    with Image.open(os.path.join('downloads', filename)) as img:
                        width, height = img.size
                        image_files_with_dims.append({
                            'filename': filename,
                            'width': width,
                            'height': height
                        })
                except FileNotFoundError:
                    # 파일이 없으면 목록에서 제외
                    print(f"Warning: Image file not found: {filename}")
                    pass
    
    # 날짜 형식 보정: created_at 대신 title에서 날짜 사용
    bulletin_date_title = post['title'].replace(' 주보', '') if post and 'title' in post else ''
    
    conn.close()
    return render_template('post.html', post=post, image_files=image_files_with_dims, prev_post=prev_post, next_post=next_post, bulletin_title=post['title'], formatted_date=bulletin_date_title)

@app.route('/list')
def list_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM weekly_posts ORDER BY created_at DESC').fetchall()
    
    # 각 주보에 이미지 파일 정보 추가
    posts_with_images = []
    for post in posts:
        post_dict = dict(post)
        image_files_with_dims = []
        if post['image_paths']:
            image_paths = post['image_paths'].split(',')
            for path in image_paths:
                filename = path.strip()
                if filename:
                    try:
                        with Image.open(os.path.join('downloads', filename)) as img:
                            width, height = img.size
                            image_files_with_dims.append({
                                'filename': filename,
                                'width': width,
                                'height': height
                            })
                    except FileNotFoundError:
                        print(f"Warning: Image file not found: {filename}")
                        pass
        post_dict['image_files'] = image_files_with_dims
        # 날짜 형식 보정: created_at 대신 title에서 날짜 사용
        bulletin_date_title = post_dict.get('title', '').replace(' 주보', '')
        post_dict['formatted_date'] = bulletin_date_title
        posts_with_images.append(post_dict)
    
    conn.close()
    return render_template('list.html', posts=posts_with_images, bulletin_title="높은뜻씨앗이되어 주보")

@app.route('/admin/verify/<int:post_id>', methods=['GET', 'POST'])
def admin_verify(post_id):
    """관리자 비밀번호 확인"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_verified'] = True
            session['post_id'] = post_id
            return redirect(url_for('admin_edit', post_id=post_id))
        else:
            flash('비밀번호가 올바르지 않습니다.', 'error')
    
    return render_template('admin_verify.html', post_id=post_id)

@app.route('/admin/edit/<int:post_id>')
def admin_edit(post_id):
    """관리자 수정 페이지"""
    if not session.get('admin_verified') or session.get('post_id') != post_id:
        return redirect(url_for('admin_verify', post_id=post_id))
    
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM weekly_posts WHERE id = ?', (post_id,)).fetchone()
    conn.close()
    
    if post is None:
        return "주보를 찾을 수 없습니다.", 404
    
    return render_template('admin_edit.html', post=post)

@app.route('/admin/save/<int:post_id>', methods=['POST'])
def admin_save(post_id):
    """관리자 수정 저장"""
    if not session.get('admin_verified') or session.get('post_id') != post_id:
        return redirect(url_for('admin_verify', post_id=post_id))
    
    ocr_data = request.form.get('ocr_data')
    
    conn = get_db_connection()
    conn.execute('UPDATE weekly_posts SET ocr_data = ? WHERE id = ?', (ocr_data, post_id))
    conn.commit()
    conn.close()
    
    flash('OCR 데이터가 성공적으로 수정되었습니다.', 'success')
    return redirect(url_for('post', post_id=post_id))

@app.route('/admin/logout')
def admin_logout():
    """관리자 로그아웃"""
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003) 