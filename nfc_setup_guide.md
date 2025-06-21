# NFC 태그 설정 가이드

## 1. NFC 태그 준비
- **NTAG213/215/216** 태그 권장 (가장 호환성이 좋음)
- 용량: 144바이트 이상 (URL 저장용)
- 구매처: 온라인 쇼핑몰, 전자제품점

## 2. NFC 태그에 URL 기록

### 방법 1: 스마트폰 앱 사용
1. **Android**: "NFC Tools" 앱 설치
2. **iOS**: "NFC Tools" 또는 "NFC TagWriter" 앱 설치
3. 태그에 터치하고 "URL" 선택
4. URL 입력: `https://your-domain.com/` (중간 포워딩 페이지 주소)
5. 태그에 기록

### 방법 2: NFC 리더/라이터 사용
- USB NFC 리더/라이터 구매
- PC용 NFC 소프트웨어 설치
- URL 기록

## 3. 배포 및 도메인 설정

### 로컬 테스트
```bash
python nfc_redirect.py
```
- 접속: `http://localhost:5004`

### 클라우드 배포 (권장)

#### Vercel 배포
1. `vercel.json` 파일 생성:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "nfc_redirect.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "nfc_redirect.py"
    }
  ]
}
```

2. Vercel CLI 설치 및 배포:
```bash
npm i -g vercel
vercel
```

#### Railway 배포
1. Railway 계정 생성
2. GitHub 저장소 연결
3. 자동 배포

#### Heroku 배포
1. `Procfile` 생성:
```
web: python nfc_redirect.py
```

2. Heroku CLI로 배포:
```bash
heroku create your-app-name
git push heroku main
```

## 4. 도메인 설정

### 무료 도메인 옵션
- **Vercel**: `your-app.vercel.app`
- **Railway**: `your-app.railway.app`
- **Heroku**: `your-app.herokuapp.com`

### 커스텀 도메인 (선택사항)
- 도메인 구매 후 DNS 설정
- CNAME 레코드로 클라우드 서비스 연결

## 5. NFC 태그 배치

### 교회 내 위치
1. **입구**: 환영 메시지와 함께
2. **안내 데스크**: 직원이 안내
3. **주보 배치대**: 주보와 함께
4. **좌석**: 각 구역별

### 태그 보호
- **라미네이션**: 투명 필름으로 보호
- **스티커**: 교회 로고와 함께 제작
- **홀더**: 플라스틱 케이스에 보관

## 6. 테스트 및 모니터링

### 테스트 방법
1. 스마트폰으로 태그 터치
2. 최신 주보로 정상 리다이렉트 확인
3. 다양한 기기에서 테스트

### 모니터링
- 접속 로그 확인
- 헬스 체크: `https://your-domain.com/health`
- 오류 발생 시 알림 설정

## 7. 사용자 안내

### 교회 웹사이트에 안내문 추가
```html
<div class="nfc-info">
  <h3>📱 NFC로 주보 보기</h3>
  <p>교회 입구의 NFC 태그를 스마트폰에 터치하면 최신 주보를 바로 볼 수 있습니다.</p>
  <ul>
    <li>Android: NFC 기능이 켜져 있어야 합니다</li>
    <li>iPhone: iOS 13 이상에서 지원됩니다</li>
  </ul>
</div>
```

### 주보에 QR코드 추가
- NFC 태그와 함께 QR코드도 제공
- QR코드: `https://your-domain.com/` 주소

## 8. 문제 해결

### 일반적인 문제
1. **태그 인식 안됨**: NFC 기능 확인
2. **리다이렉트 안됨**: 서버 상태 확인
3. **느린 로딩**: 교회 웹사이트 응답 시간 확인

### 백업 방안
- QR코드 병행 사용
- 수동 링크 제공
- 주보 게시판 직접 안내 