# 시놀로지 서버 자동 업데이트 설정 가이드

## 🚀 시놀로지 서버 활용 방법

### 1단계: 시놀로지에 Python 환경 설정
```bash
# SSH로 시놀로지 접속
ssh admin@your-synology-ip

# Python 설치 (이미 설치되어 있을 수 있음)
sudo synopkg install Python3

# 필요한 패키지 설치
pip3 install requests beautifulsoup4
```

### 2단계: 프로젝트 파일 업로드
```bash
# 시놀로지에 프로젝트 폴더 생성
mkdir -p /volume1/web/gwseed-weekly
cd /volume1/web/gwseed-weekly

# GitHub에서 파일 다운로드
wget https://raw.githubusercontent.com/your-username/your-repo-name/main/auto_update_script.py
wget https://raw.githubusercontent.com/your-username/your-repo-name/main/index.html
wget https://raw.githubusercontent.com/your-username/your-repo-name/main/latest_bulletin.json
```

### 3단계: Git 설정
```bash
# Git 설치
sudo synopkg install Git

# 저장소 클론
git clone https://github.com/purplestory/gwseed-bulletin-nfc.git
cd gwseed-bulletin-nfc

# Git 인증 설정
git config --global user.name "Synology Bot"
git config --global user.email "synology@example.com"
```

### 4단계: 자동 실행 스크립트 생성
```bash
# update_script.sh 생성
cat > update_script.sh << 'EOF'
#!/bin/bash
cd /volume1/web/gwseed-bulletin-nfc

# Python 스크립트 실행
python3 auto_update_script.py

# 변경사항이 있으면 Git 커밋 및 푸시
if [[ -n "$(git status --porcelain)" ]]; then
    git add index.html latest_bulletin.json
    # 썸네일 이미지가 있으면 추가
    if [ -f "assets/thumbnail_2026.jpg" ]; then
      git add assets/thumbnail_2026.jpg
    fi
    git commit -m "Auto update from Synology $(date +'%Y-%m-%d %H:%M:%S')"
    git pull origin main --rebase
    git push origin main
    echo "Changes committed and pushed successfully"
else
    echo "No changes detected"
fi
EOF

chmod +x update_script.sh
```

### 5단계: Cron 작업 설정
```bash
# crontab 편집
crontab -e

# 토요일 오후 3시, 6시 실행
0 15 * * 6 /volume1/web/gwseed-bulletin-nfc/update_script.sh
0 18 * * 6 /volume1/web/gwseed-bulletin-nfc/update_script.sh
```

## 🎯 장점

1. **국내 IP 주소** - 봇 차단 우회 가능성 높음
2. **실제 서버 환경** - GitHub Actions와 달리 안정적
3. **JavaScript 실행 가능** - 봇 차단 스크립트 실행
4. **24/7 실행** - 지속적인 자동 업데이트
5. **비용 효율적** - 기존 시놀로지 서버 활용

## ⚠️ 주의사항

1. **Git 인증** - Personal Access Token 설정 필요
2. **네트워크 안정성** - 인터넷 연결 확인
3. **로그 모니터링** - 실행 결과 확인
4. **백업** - 중요한 파일 백업

## 🔧 문제 해결

### Git 인증 오류 시:
```bash
# Personal Access Token으로 인증
git remote set-url origin https://your-token@github.com/purplestory/gwseed-bulletin-nfc.git
```

### 스토리지 문제 해결 후:
```bash
# 저장소 경로 확인
cd /volume1/web/gwseed-bulletin-nfc

# Git 상태 확인
git status

# 최신 코드 가져오기
git pull origin main

# 스크립트 실행 권한 확인
chmod +x update_script.sh
chmod +x auto_update_script.py

# Cron 작업 확인
crontab -l
```

### 실행 권한 오류 시:
```bash
chmod +x update_script.sh
chmod +x auto_update_script.py
``` 