# 수동 주보 업데이트 가이드

## 🚨 자동 업데이트 실패 시 수동 업데이트 방법

### 1단계: 최신 주보 확인
1. **https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly** 접속
2. **최신 주보의 wr_id 확인** (URL에서 `wr_id=숫자` 부분)

### 2단계: 로컬 파일 업데이트
```bash
# index.html 파일에서 wr_id 업데이트
# 예: wr_id=740을 wr_id=741로 변경
```

### 3단계: GitHub에 커밋 및 푸시
```bash
git add index.html latest_bulletin.json
git commit -m "수동 업데이트: 최신 주보 wr_id=741"
git push origin main
```

### 4단계: 배포 확인
- **1-2분 후** http://gwseed-bulletin-nfc.vercel.app 접속
- **최신 주보로 리다이렉트**되는지 확인

## 📋 현재 설정
- **현재 wr_id**: 742
- **마지막 업데이트**: 2025년 8월 4일

## 🔄 자동 업데이트 스케줄
- **토요일 오후 3시, 6시** (한국시간)
- **GitHub Actions에서 자동 실행**
- **봇 차단으로 인해 수동 확인 필요** 