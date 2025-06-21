# 자동 업데이트 설정 가이드

## 방법 1: 로컬 Cron Job (권장)

### 1. 스크립트 실행 권한 부여
```bash
chmod +x auto_update_script.py
```

### 2. Cron Job 설정
```bash
# crontab 편집
crontab -e

# 다음 줄 추가 (매주 일요일 오전 9시 실행)
0 9 * * 0 cd /Users/psilvu/Dev/GwSeedWeekly && python auto_update_script.py
```

### 3. Cron Job 확인
```bash
crontab -l
```

## 방법 2: GitHub Actions (대안)

### 1. .github/workflows/auto-update.yml 파일 생성
```yaml
name: Auto Update Latest Bulletin

on:
  schedule:
    # 매주 일요일 오전 9시 (UTC)
    - cron: '0 9 * * 0'
  workflow_dispatch: # 수동 실행 가능

jobs:
  update-bulletin:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install requests beautifulsoup4
    
    - name: Run auto update script
      run: python auto_update_script.py
    
    - name: Commit and push changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add index.html
        git commit -m "Auto update latest bulletin" || exit 0
        git push
```

## 방법 3: Vercel Cron Jobs (현재 설정됨)

### 현재 설정
- **스케줄**: 매주 일요일 오전 9시
- **API 엔드포인트**: `/api/update-latest`
- **자동 배포**: GitHub 푸시 시

### 수동 실행
```bash
curl -X POST https://gwseed-bulletin-nfc.vercel.app/api/update-latest
```

## 테스트

### 1. 수동 실행 테스트
```bash
python auto_update_script.py
```

### 2. 결과 확인
```bash
# index.html에서 wr_id 확인
grep "wr_id=" index.html

# Git 상태 확인
git status
```

## 문제 해결

### Cron Job이 실행되지 않는 경우
1. **로그 확인**: `tail -f /var/log/cron`
2. **경로 확인**: 절대 경로 사용
3. **권한 확인**: 스크립트 실행 권한

### GitHub Actions가 실패하는 경우
1. **Actions 탭 확인**: GitHub 저장소에서 확인
2. **로그 확인**: 실패 원인 파악
3. **수동 실행**: workflow_dispatch 사용

## 권장 설정

### 로컬 환경 (개발자용)
- **Cron Job**: 매주 일요일 오전 9시
- **백업**: GitHub Actions와 병행

### 서버 환경 (운영용)
- **GitHub Actions**: 자동화된 워크플로우
- **Vercel Cron**: 추가 백업

## 현재 상태
- ✅ **Vercel Cron**: 설정됨 (매주 일요일 오전 9시)
- ✅ **자동 스크립트**: 준비됨
- ⚠️ **로컬 Cron**: 설정 필요
- ⚠️ **GitHub Actions**: 설정 필요 