# 🎵 YouTube 다운로더

## 개요

모바일 최적화된 YouTube 다운로더 웹 애플리케이션입니다. 다양한 형식(MP3, MP4, M4A, WEBM)으로 YouTube 콘텐츠를 다운로드할 수 있으며, Android 및 iOS 모바일 브라우저에서 완벽하게 작동합니다.

## 주요 기능

### 🎬 다운로드 기능
- **다양한 형식 지원**: MP3, MP4, M4A, WEBM
- **품질 선택**: 128k~320k (오디오), 360p~1080p (비디오)
- **브라우저 직접 다운로드**: 서버 저장 없이 브라우저에서 바로 다운로드
- **모바일 최적화**: Android/iOS 브라우저 완벽 호환

### 🔍 검색 기능
- **YouTube 검색**: 키워드로 비디오 검색
- **인기 추천**: DAY6, 유요 등 인기 콘텐츠 원클릭 검색
- **미리보기**: 썸네일 클릭으로 비디오 미리보기
- **상세 정보**: 채널명, 업로드일, 설명 표시

### 📱 모바일 지원
- **터치 최적화**: 큰 버튼과 입력창으로 터치 친화적
- **반응형 디자인**: 다양한 화면 크기 자동 적응
- **다운로드 가이드**: Android/iOS별 상세한 사용법 제공

## 기술 스택

- **Frontend**: Streamlit 웹 프레임워크
- **Backend**: Python 3.11
- **다운로드 엔진**: yt-dlp (youtube-dl 개선 버전)
- **API**: YouTube Data API v3
- **오디오/비디오 처리**: FFmpeg

## 설치 및 실행

### 로컬 환경

```bash
# 저장소 클론
git clone <repository-url>
cd youtube-downloader

# 의존성 설치
uv add yt-dlp google-api-python-client streamlit

# FFmpeg 설치 (시스템에 따라)
# Ubuntu/Debian: sudo apt install ffmpeg
# macOS: brew install ffmpeg
# Windows: https://ffmpeg.org/download.html

# 애플리케이션 실행
streamlit run app.py --server.port 5000
```

### Replit 배포

1. Replit에서 새 Python 프로젝트 생성
2. 코드 업로드
3. `packages.txt`에 `ffmpeg` 추가
4. Run 버튼 클릭

### Streamlit Cloud 배포

1. GitHub 저장소에 코드 푸시
2. [Streamlit Cloud](https://streamlit.io/cloud) 접속
3. 저장소 연결 및 배포

## 파일 구조

```
youtube-downloader/
├── app.py              # 메인 Streamlit 애플리케이션
├── downloader.py       # YouTube 다운로드 로직
├── utils.py           # 유틸리티 함수
├── packages.txt       # 시스템 의존성 (ffmpeg)
├── pyproject.toml     # Python 프로젝트 설정
├── replit.md          # 프로젝트 문서
└── README.md          # 이 파일
```

## API 키 설정

YouTube 검색 기능을 사용하려면 YouTube Data API 키가 필요합니다:

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성 또는 기존 프로젝트 선택
3. YouTube Data API v3 활성화
4. API 키 생성
5. `app.py`의 `api_key` 변수에 키 입력

## 사용법

### 기본 다운로드

1. YouTube URL 입력 탭에서 비디오 URL 입력
2. "URL 확인" 버튼 클릭하여 비디오 정보 확인
3. 원하는 형식과 품질 선택
4. "다운로드 시작" 버튼 클릭
5. 완료 후 다운로드 버튼으로 파일 저장

### 검색을 통한 다운로드

1. YouTube 검색 탭 선택
2. 검색어 입력 또는 "인기 추천" 버튼 클릭
3. 원하는 비디오에서 "선택" 버튼 클릭
4. URL 입력 탭으로 자동 이동하여 다운로드 진행

### 모바일에서 사용

**Android:**
- 다운로드 버튼 탭하면 다운로드 폴더에 자동 저장

**iOS:**
- 다운로드 버튼 길게 눌러서 "파일에 저장" 선택

## 기능 상세

### 지원 형식

| 형식 | 확장자 | 품질 옵션 | 용도 |
|------|---------|-----------|------|
| MP3 | .mp3 | 128k, 192k, 320k | 음악 감상 |
| M4A | .m4a | 128k, 192k, 320k | 고품질 오디오 |
| MP4 | .mp4 | 360p, 480p, 720p, 1080p | 비디오 시청 |
| WEBM | .webm | 360p, 480p, 720p, 1080p | 웹 최적화 |

### 성능 최적화

- **Streamlit Cloud 적합**: 메모리 및 처리 시간 제한 고려
- **재생목록 제한**: 성능상 첫 번째 비디오만 다운로드
- **임시 파일 관리**: 다운로드 후 자동 정리
- **진행률 표시**: 실시간 다운로드 상태 확인

## 브라우저 호환성

### 데스크톱
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### 모바일
- Chrome Mobile 90+
- Safari iOS 14+
- Samsung Internet 15+
- Firefox Mobile 88+

## 문제 해결

### 다운로드 실패
1. 인터넷 연결 확인
2. YouTube URL 유효성 확인
3. 브라우저 새로고침 후 재시도

### 모바일 다운로드 문제
1. 최신 브라우저 사용 확인
2. 저장 공간 확인
3. 데이터/Wi-Fi 연결 상태 확인

### API 오류
1. YouTube API 키 유효성 확인
2. API 할당량 제한 확인
3. 네트워크 연결 상태 확인

## 개발자 정보

**개발자**: 조성우 (Sungwoo Cho)  
**연락처**: [GitHub Profile]  
**라이선스**: 개인 및 교육용 사용만 허용  

## 주의사항

- 이 애플리케이션은 개인 및 교육 목적으로만 사용해야 합니다
- 저작권이 있는 콘텐츠 다운로드 시 관련 법규를 준수하세요
- YouTube 서비스 약관을 확인하고 준수하세요
- 상업적 이용은 금지됩니다

## 기여

버그 리포트나 기능 제안은 GitHub Issues를 통해 제출해 주세요.

## 업데이트 로그

- **2025.06.26**: 초기 버전 릴리스
- **2025.06.26**: FFmpeg 의존성 해결, 모바일 최적화 완료
- **2025.06.26**: YouTube 봇 검증 우회 기능 추가