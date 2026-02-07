# 시놀로지 서버 자동 업데이트 설정 가이드

## 🚀 시놀로지 서버 활용 방법

### 1단계: 시놀로지에 Python 환경 설정
```bash
# SSH로 시놀로지 접속
ssh admin@your-synology-ip

# Python 설치 방법 (시놀로지 버전에 따라 다름)
# 방법 1: 패키지 센터에서 설치 (권장)
# - 시놀로지 DSM 웹 인터페이스 접속
# - 패키지 센터 열기
# - "Python 3" 검색 후 설치

# 방법 2: 이미 설치되어 있는지 확인
python3 --version
# 또는
python --version

# 방법 3: Python3가 없으면 pip3로 설치 시도
# (일부 시놀로지 모델은 Python이 기본 설치되어 있음)

# 필요한 패키지 설치
pip3 install requests beautifulsoup4
# 또는 pip가 없으면
python3 -m ensurepip --upgrade
python3 -m pip install requests beautifulsoup4
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

## 🔍 시놀로지 크론이 업데이트를 안 했을 때 확인 사항

업데이트가 멈춘 것 같다면 아래를 순서대로 확인하세요.

### DSM 웹 인터페이스에서 확인하기 (SSH 없이)

DSM(시놀로지 웹 관리 페이지)에서 아래처럼 확인할 수 있습니다.

#### 1. 작업 스케줄러에서 크론 확인
1. DSM 로그인 → **제어판** → **작업 스케줄러**
2. **생성** → **예약된 작업** → **사용자 정의 스크립트** 선택
3. 기존에 등록한 "주보 업데이트" 같은 작업이 있는지 확인
4. **일정** 탭: 토요일 15:00, 18:00 등으로 설정되어 있는지 확인
5. **작업 설정** 탭: 사용자 `root` 또는 `admin`, 스크립트에 `/volume1/web/gwseed-bulletin-nfc/update_script.sh` 경로가 있는지 확인

**참고:** SSH `crontab`과 DSM 작업 스케줄러는 별도입니다. SSH로 `crontab -e`로 등록했다면 DSM 작업 스케줄러에는 보이지 않습니다. 둘 중 한 곳에만 등록되어 있어야 중복 실행을 막을 수 있습니다.

#### 2. 수동 실행으로 동작 여부 확인
1. **제어판** → **작업 스케줄러**
2. **생성** → **트리거된 작업** → **사용자 정의 스크립트**
3. 작업 이름: `주보 업데이트 테스트`
4. **작업 설정** 탭 → 사용자 `root` 선택  
   실행 명령:  
   `/bin/bash -c "cd /volume1/web/gwseed-bulletin-nfc && ./update_script.sh"`
5. **확인** 후, 작업 목록에서 해당 작업 선택 → **실행** 클릭
6. 실행 결과는 SSH 없이는 직접 볼 수 없으므로, **아래 3번**처럼 로그를 켜 두고 File Station에서 `update.log`를 확인하는 것이 좋습니다.

#### 3. 로그 파일 확인 (File Station)
1. `update_script.sh`를 가이드대로 로그를 남기도록 수정했다면
2. DSM → **File Station** → `web` → `gwseed-bulletin-nfc` 폴더 이동
3. `update.log` 파일이 있으면 **다운로드** 후 열어서 마지막 실행 시간, 에러 메시지 확인

#### 4. 작업 스케줄러로 크론 대체 (SSH 대신 DSM에서 등록)
SSH를 쓰지 않고 DSM에서 스케줄만 설정하려면:

1. **제어판** → **작업 스케줄러** → **생성** → **예약된 작업** → **사용자 정의 스크립트**
2. 일반: 이름 `주보 자동 업데이트 15시`
3. 일정: **주기적으로** → **매주** → 요일 **토요일** 선택 → 시간 **15:00**
4. 작업 설정: 사용자 `root`, 스크립트  
   `/volume1/web/gwseed-bulletin-nfc/update_script.sh`
5. **확인** 후 저장  
6. 동일하게 18시용 작업(`주보 자동 업데이트 18시`) 하나 더 생성

---

### 1. 크론 등록 여부 (SSH)
```bash
crontab -l
```
- `0 15 * * 6` / `0 18 * * 6` 항목이 있는지 확인
- **주의:** 크론은 로그인한 사용자 계정에만 등록됨. 다른 사용자로 SSH 접속했으면 해당 사용자 crontab도 확인

### 2. 수동 실행으로 동작 여부 확인
```bash
cd /volume1/web/gwseed-bulletin-nfc
./update_script.sh
```
- 여기서 실패하면 크론에서도 실패함
- **Python 실패:** `python3` 없음 → 패키지 센터에서 Python3 설치 또는 `which python3`로 경로 확인 후 스크립트 shebang/경로 수정
- **교회 사이트 접근 실패:** "모든 User-Agent 시도가 실패" → 봇 차단 가능성. 아래 4번 참고

### 3. 크론 실행 시 로그 남기기 (원인 파악용)
`update_script.sh`를 아래처럼 수정하면 실행 결과를 로그 파일로 남길 수 있음:
```bash
#!/bin/bash
LOG="/volume1/web/gwseed-bulletin-nfc/update.log"
cd /volume1/web/gwseed-bulletin-nfc
{
  echo "=== $(date) ==="
  python3 auto_update_script.py
  if [[ -n "$(git status --porcelain)" ]]; then
    git add index.html latest_bulletin.json
    [ -f "assets/thumbnail_2026.jpg" ] && git add assets/thumbnail_2026.jpg
    git commit -m "Auto update from Synology $(date +'%Y-%m-%d %H:%M')"
    git pull origin main --rebase
    git push origin main
    echo "Changes pushed"
  else
    echo "No changes"
  fi
} >> "$LOG" 2>&1
```
- 다음 토요일 크론 실행 후 `cat /volume1/web/gwseed-bulletin-nfc/update.log` 로 실패 메시지 확인

### 4. 교회 사이트 봇 차단 가능성
- 교회 사이트가 요청을 봇으로 판단해 HTML에서 `wr_id`를 주지 않으면 스크립트는 "주보 링크를 찾을 수 없습니다"로 끝남
- 시놀로지에서 브라우저로는 접속되는데 스크립트만 실패하면 차단일 수 있음
- 대안: 수동으로 주보 페이지에서 최신 `wr_id` 확인 후 `curl -X POST https://gwseed-bulletin-nfc.vercel.app/api/update-latest` 로 Vercel API 한 번 호출해 갱신

### 5. Git 푸시 실패
- 토큰 만료: GitHub Personal Access Token 재발급 후 `git remote set-url origin https://새토큰@github.com/purplestory/gwseed-bulletin-nfc.git`
- push 시 conflict: 수동으로 `git pull --rebase origin main` 후 `git push origin main` 실행해 보기 