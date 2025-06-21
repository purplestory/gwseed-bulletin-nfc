# NFC 주보 관리자 가이드

## 최신 주보 업데이트 방법

### 1. **자동 업데이트 (권장)**
매주 일요일 오전 9시에 자동으로 최신 주보를 확인합니다.
- Vercel Cron Jobs가 자동 실행
- 별도 작업 불필요

### 2. **수동 업데이트 (필요시)**

#### 방법 1: 웹 브라우저에서 업데이트
```
https://gwseed-bulletin-nfc.vercel.app/update/733
```
- `733` 부분을 새로운 wr_id로 변경
- 예: 최신 주보가 wr_id=733이면 `/update/733`

#### 방법 2: API 직접 호출
```bash
curl -X POST https://gwseed-bulletin-nfc.vercel.app/api/update-latest
```

### 3. **최신 주보 확인 방법**

#### 교회 웹사이트에서 확인
1. [교회 주보 게시판](https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly) 접속
2. 가장 위쪽 게시물의 URL에서 `wr_id` 확인
3. 예: `wr_id=733`이면 최신 주보

#### 현재 설정 확인
```
https://gwseed-bulletin-nfc.vercel.app/health
```

## 주보 업데이트 절차

### 매주 일요일 오전
1. **교회 웹사이트 확인**
   - 새로운 주보가 업로드되었는지 확인
   - URL에서 `wr_id` 번호 확인

2. **자동 업데이트 확인**
   - NFC 태그로 테스트
   - 최신 주보로 이동하는지 확인

3. **수동 업데이트 (필요시)**
   - 자동 업데이트가 실패한 경우
   - `/update/{wr_id}` URL로 수동 업데이트

## 문제 해결

### NFC 태그가 리스트로만 이동하는 경우
1. 최신 주보 URL 확인
2. 수동 업데이트 실행
3. 헬스 체크로 현재 설정 확인

### 자동 업데이트가 실패하는 경우
- 교회 웹사이트 보안 정책으로 인한 차단
- 수동 업데이트 사용

## 현재 설정
- **최신 주보**: wr_id=732
- **URL**: https://www.godswillseed.or.kr/bbs/board.php?bo_table=weekly&wr_id=732
- **업데이트 시간**: 매주 일요일 오전 9시 