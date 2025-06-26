import streamlit as st
import os
import tempfile
import base64
import time
import threading
from pathlib import Path
import shutil
from downloader import YouTubeDownloader
from utils import sanitize_filename, validate_youtube_url, format_bytes, get_video_info
try:
    from googleapiclient.discovery import build
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False

# 페이지 설정
st.set_page_config(
    page_title="YouTube 다운로더",
    page_icon="📹",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 모바일 최적화 CSS (라이트 테마)
st.markdown("""
<style>
    /* 모바일 최적화 */
    .main > div {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* 버튼 크기 증가 (모바일 터치 최적화) */
    .stButton > button {
        height: 3rem;
        width: 100%;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 15px;
        margin: 0.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* 입력 필드 크기 증가 */
    .stTextInput > div > div > input {
        height: 3rem;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 15px;
        border: 2px solid #e0e6ed;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 선택 박스 크기 증가 */
    .stSelectbox > div > div > select {
        height: 3rem;
        font-size: 1.1rem;
        padding: 0.5rem;
        border-radius: 15px;
        border: 2px solid #e0e6ed;
    }
    
    /* 제목 및 텍스트 크기 최적화 */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .section-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin: 1.5rem 0 1rem 0;
        color: #4a5568;
        border-bottom: 3px solid #667eea;
        padding-bottom: 0.5rem;
        display: inline-block;
    }
    
    /* 진행 상황 바 스타일 */
    .progress-container {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #e0e6ed;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    }
    
    /* 비디오 정보 카드 */
    .video-info {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
        border: 1px solid #e0e6ed;
    }
    
    /* 기능 카드 */
    .feature-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
        border: 1px solid #e0e6ed;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    /* 오류 메시지 */
    .error-message {
        background: linear-gradient(135deg, #fc8181 0%, #f56565 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(245, 101, 101, 0.3);
    }
    
    /* 성공 메시지 */
    .success-message {
        background: linear-gradient(135deg, #68d391 0%, #48bb78 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.3);
    }
    
    /* 경고 메시지 */
    .warning-message {
        background: linear-gradient(135deg, #fbb034 0%, #f6ad55 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(251, 176, 52, 0.3);
    }
    
    /* 정보 메시지 */
    .info-message {
        background: linear-gradient(135deg, #63b3ed 0%, #4299e1 100%);
        color: white;
        padding: 1.2rem;
        border-radius: 15px;
        margin: 1rem 0;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(66, 153, 225, 0.3);
    }
    
    /* 썸네일 이미지 */
    .thumbnail {
        border-radius: 20px;
        width: 100%;
        max-width: 400px;
        height: auto;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        border: 3px solid #ffffff;
    }
    
    /* 통계 카드 */
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
    }
    
    .stats-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }
    
    .stats-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* 푸터 스타일 */
    .footer {
        background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
        border-radius: 20px;
        padding: 2rem;
        margin-top: 3rem;
        text-align: center;
        border: 1px solid #e0e6ed;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    
    .developer-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    /* 체크박스 스타일 */
    .stCheckbox > label > div:first-child {
        border-radius: 8px;
        border: 2px solid #667eea;
    }
    
    /* 반응형 열 */
    @media (max-width: 768px) {
        .main-title {
            font-size: 2.2rem;
        }
        .section-title {
            font-size: 1.4rem;
        }
        .feature-card {
            padding: 1rem;
        }
        .stats-card {
            margin: 0.25rem;
            padding: 1rem;
        }
    }
    
    /* 애니메이션 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .animate-fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'download_progress' not in st.session_state:
    st.session_state.download_progress = 0
if 'download_status' not in st.session_state:
    st.session_state.download_status = ""
if 'video_info' not in st.session_state:
    st.session_state.video_info = None
if 'download_complete' not in st.session_state:
    st.session_state.download_complete = False
if 'download_file_path' not in st.session_state:
    st.session_state.download_file_path = None
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'selected_video_url' not in st.session_state:
    st.session_state.selected_video_url = ""

def progress_hook(d):
    """다운로드 진행 상황 업데이트"""
    if d['status'] == 'downloading':
        try:
            downloaded_bytes = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total_bytes > 0:
                progress = int((downloaded_bytes / total_bytes) * 100)
                st.session_state.download_progress = progress
                speed = d.get('speed', 0)
                if speed:
                    speed_str = format_bytes(speed) + "/s"
                    st.session_state.download_status = f"다운로드 중... {progress}% ({speed_str})"
                else:
                    st.session_state.download_status = f"다운로드 중... {progress}%"
        except Exception as e:
            st.session_state.download_status = "다운로드 중..."
    elif d['status'] == 'finished':
        st.session_state.download_progress = 100
        st.session_state.download_status = "다운로드 완료! 파일 처리 중..."
        st.session_state.download_complete = True
        st.session_state.download_file_path = d['filename']

def create_download_link(file_path, filename):
    """파일 다운로드 링크 생성"""
    try:
        with open(file_path, "rb") as f:
            bytes_data = f.read()
        b64 = base64.b64encode(bytes_data).decode()
        href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}" style="text-decoration: none;"><button style="background-color: #4caf50; color: white; padding: 1rem 2rem; border: none; border-radius: 10px; font-size: 1.1rem; font-weight: bold; cursor: pointer; width: 100%; margin: 1rem 0;">📥 {filename} 다운로드</button></a>'
        return href
    except Exception as e:
        st.error(f"다운로드 링크 생성 중 오류: {str(e)}")
        return None

def search_youtube_videos(query, max_results=10):
    """YouTube에서 비디오 검색"""
    if not YOUTUBE_API_AVAILABLE:
        return []
    
    api_key = 'AIzaSyA6t6CCcgax92EtnfKChWsVTYM4l19NcWg'
    if not api_key:
        return []
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results,
            type='video',
            order='relevance'
        ).execute()
        
        videos = []
        for search_result in search_response.get('items', []):
            video_id = search_result['id']['videoId']
            snippet = search_result['snippet']
            
            video_info = {
                'id': video_id,
                'title': snippet['title'],
                'channel': snippet['channelTitle'],
                'thumbnail': snippet['thumbnails']['medium']['url'],
                'description': snippet['description'][:100] + '...' if len(snippet['description']) > 100 else snippet['description'],
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'published': snippet['publishedAt'][:10]  # YYYY-MM-DD 형식
            }
            videos.append(video_info)
        
        return videos
    except Exception as e:
        st.error(f"검색 중 오류가 발생했습니다: {str(e)}")
        return []

def main():
    # 메인 제목
    st.markdown('<h1 class="main-title animate-fade-in">🎵 YouTube 다운로더</h1>', unsafe_allow_html=True)
    
    # 탭 생성
    tab1, tab2 = st.tabs(["🔗 URL 입력", "🔍 YouTube 검색"])
    
    with tab1:
        # URL 입력 섹션
        st.subheader("YouTube URL 입력")
        
        # 자동 URL 처리 및 선택된 비디오 URL 처리
        default_url = ""
        if 'selected_video_url' in st.session_state and st.session_state.selected_video_url:
            default_url = st.session_state.selected_video_url
            st.session_state.selected_video_url = ""
            st.info("🎵 검색에서 선택한 비디오가 자동으로 입력되었습니다!")
        elif 'auto_url' in st.session_state:
            default_url = st.session_state.auto_url
            del st.session_state.auto_url
        
        url_input = st.text_input(
            "YouTube URL",
            value=default_url,
            placeholder="https://www.youtube.com/watch?v=... 또는 https://youtu.be/...",
            help="YouTube 비디오 또는 재생목록 URL을 입력하세요",
            label_visibility="collapsed"
        )
        
        if st.button("🔍 URL 확인", use_container_width=True):
            if url_input.strip():
                if validate_youtube_url(url_input.strip()):
                    with st.spinner("비디오 정보를 가져오는 중..."):
                        video_info = get_video_info(url_input.strip())
                        if video_info:
                            st.session_state.video_info = video_info
                            st.success("유효한 YouTube URL입니다!")
                        else:
                            st.error("비디오 정보를 가져올 수 없습니다.")
                else:
                    st.error("올바른 YouTube URL을 입력해주세요.")
            else:
                st.warning("URL을 입력해주세요.")
    
    with tab2:
        # YouTube 검색 섹션
        st.subheader("YouTube 검색")
        
        if not YOUTUBE_API_AVAILABLE:
            st.error("YouTube 검색 기능을 사용하려면 google-api-python-client 패키지가 필요합니다.")
            return
        
        api_key = 'AIzaSyA6t6CCcgax92EtnfKChWsVTYM4l19NcWg'
        if not api_key:
            st.warning("YouTube API 키가 설정되지 않았습니다. 검색 기능을 사용하려면 YOUTUBE_API_KEY를 설정해주세요.")
            return
        
        search_query = st.text_input("검색어를 입력하세요", placeholder="예: 겨울왕국 let it go")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button("🔍 검색", use_container_width=True):
                if search_query.strip():
                    with st.spinner("YouTube에서 검색 중..."):
                        results = search_youtube_videos(search_query.strip())
                        st.session_state.search_results = results
                else:
                    st.warning("검색어를 입력해주세요.")
        
        with col2:
            if st.button("🎵 인기 추천", use_container_width=True):
                # 더 다양한 인기 음악 리스트
                popular_songs = [
                    "DAY6 - HAPPY", "DAY6 - Welcome to the show", "DAY6 - 예뻤어", "DAY6 - Congratulations",
                    "DAY6 - 뚫고 지나가요", "DAY6 - Zombie", "DAY6 - 놓아 놓아 놓아", "DAY6 - 행복했던 날들이었다",
                    "DAY6 - 좋아합니다", "DAY6 - 한 페이지가 될 수 있게", "DAY6 - 녹아내려요", "DAY6 - 어떻게 말해",
                    "DAY6 - Shoot me", "DAY6 - Beautiful feeling", "DAY6 - Sweet Chaos", "DAY6 - 반드시 웃는다",
                    "유요 - 6.25 전쟁 요약 노래", "유요 - 조선 왕 이름 외우기", "유요 - 고려 왕 이름 외우기", "유요 - 서울의 봄 요약 노래"
                ]
                import random
                selected = random.choice(popular_songs)
                with st.spinner(f"'{selected}' 검색 중..."):
                    results = search_youtube_videos(selected)
                    st.session_state.search_results = results
                    st.success(f"'{selected}' 검색 완료!")
        
        # 검색 결과 표시
        if st.session_state.search_results:
            st.subheader(f"검색 결과 ({len(st.session_state.search_results)}개)")
            
            for idx, video in enumerate(st.session_state.search_results):
                with st.container():
                    col1, col2, col3 = st.columns([1, 2, 1])
                    
                    with col1:
                        # 썸네일을 클릭하면 미리보기 토글
                        if st.button("▶️", key=f"thumb_{idx}", help="클릭하여 미리보기"):
                            st.session_state[f"show_preview_{idx}"] = not st.session_state.get(f"show_preview_{idx}", False)
                        st.image(video['thumbnail'], use_container_width=True)
                    
                    with col2:
                        st.markdown(f"**{video['title']}**")
                        st.markdown(f"채널: {video['channel']}")
                        st.markdown(f"업로드: {video['published']}")
                        st.markdown(f"[YouTube에서 보기]({video['url']})")
                        if video['description']:
                            st.caption(video['description'])
                    
                    with col3:
                        # 선택 버튼과 빠른 다운로드 버튼
                        if st.button("✅ 선택", key=f"select_{idx}", use_container_width=True, type="primary"):
                            st.session_state.selected_video_url = video['url']
                            try:
                                import pyperclip
                                pyperclip.copy(video['url'])
                            except:
                                pass
                            st.success(f"'{video['title']}' 선택됨!")
                            st.balloons()
                        
                        # 빠른 MP3 다운로드 버튼
                        # if st.button("🎵 MP3", key=f"quick_mp3_{idx}", help="바로 MP3 다운로드"):
                        #     st.session_state.quick_download = {
                        #         'url': video['url'],
                        #         'format': 'mp3',
                        #         'title': video['title']
                        #     }
                        #     st.rerun()
                        
                        # # 빠른 MP4 다운로드 버튼  
                        # if st.button("🎬 MP4", key=f"quick_mp4_{idx}", help="바로 MP4 다운로드"):
                        #     st.session_state.quick_download = {
                        #         'url': video['url'],
                        #         'format': 'mp4', 
                        #         'title': video['title']
                        #     }
                        #     st.rerun()
                    
                    # 썸네일 클릭 시 미리보기
                    if st.session_state.get(f"show_preview_{idx}", False):
                        video_id = video['id']
                        embed_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&rel=0"
                        st.markdown(f'''
                        <div style="border-radius: 12px; overflow: hidden; margin: 1rem 0; 
                                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                            <iframe width="100%" height="315" 
                                src="{embed_url}" 
                                frameborder="0" 
                                allowfullscreen>
                            </iframe>
                        </div>
                        ''', unsafe_allow_html=True)
                    
                    st.markdown("---")
    
    # 비디오 정보 표시
    if st.session_state.video_info:
        info = st.session_state.video_info
        st.markdown('<h2 class="section-title">📺 비디오 정보</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if info.get('thumbnail'):
                st.image(info['thumbnail'], use_container_width=True)
        
        with col2:
            st.markdown(f"""
            <div class="video-info">
                <h3 style="margin-top: 0; color: #667eea;">{info.get('title', 'N/A')}</h3>
                <p><strong>📺 채널:</strong> {info.get('uploader', 'N/A')}</p>
                <p><strong>👀 조회수:</strong> {info.get('view_count', 0):,}회</p>
                <p><strong>⏱️ 길이:</strong> {info.get('duration_string', 'N/A')}</p>
                {f"<p><strong>📋 재생목록:</strong> {info.get('playlist_count', 0)}개 비디오</p>" if info.get('playlist_count') else ""}
            </div>
            """, unsafe_allow_html=True)
        
        # 다운로드 설정
        st.subheader("⚙️ 다운로드 설정")
        
        # 파일 형식 선택
        format_type = st.selectbox(
            "📁 파일 형식 선택",
            ["MP3 (음성만)", "MP4 (비디오)", "M4A (고품질 음성)", "WEBM (고효율 비디오)"]
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if format_type in ["MP3 (음성만)", "M4A (고품질 음성)"]:
                quality = st.selectbox(
                    "🎵 음질",
                    ["128k (표준)", "192k (고품질)", "320k (최고품질)"],
                    index=1
                )
            else:
                quality = st.selectbox(
                    "🎬 화질 (Streamlit Cloud 최적화)",
                    ["360p (모바일)", "480p (표준)", "720p (HD)", "1080p (풀HD)"],
                    index=2,
                    help="4K/2K는 Streamlit Cloud 제한으로 지원되지 않습니다."
                )
        
        with col2:
            # 다운로드 속도 옵션
            speed_option = st.selectbox(
                "⚡ 속도",
                ["표준", "고속", "최고품질"]
            )
        
        with col3:
            # 파일명 옵션
            filename_option = st.selectbox(
                "📝 파일명",
                ["자동", "간단", "상세"]
            )
        
        # 추가 옵션들
        col1, col2 = st.columns(2)
        
        with col1:
            # 재생목록 옵션
            if info.get('playlist_count'):
                playlist_option = st.checkbox(f"📝 전체 재생목록 다운로드 ({info.get('playlist_count')}개)")
            else:
                playlist_option = False
            
            # 파일명 커스터마이징
            custom_filename = st.text_input("📝 커스텀 파일명 (선택사항)", placeholder="원하는 파일명 입력...")
        
        with col2:
            # 오디오 품질 향상 옵션
            enhance_audio = st.checkbox("🎵 오디오 품질 향상", help="노이즈 감소 및 음질 개선")
            
            # 자동 태그 추가
            auto_tags = st.checkbox("🏷️ 자동 메타데이터 태그", value=True, help="제목, 아티스트 등 자동 태그")
        
        if st.button("🚀 다운로드 시작", use_container_width=True, type="primary"):
            if url_input.strip():
                # 다운로드 진행 상황 초기화
                st.session_state.download_progress = 0
                st.session_state.download_status = "다운로드 준비 중..."
                st.session_state.download_complete = False
                st.session_state.download_file_path = None
                
                # 임시 디렉토리 생성
                temp_dir = tempfile.mkdtemp()
                
                try:
                    # 다운로드 설정
                    downloader = YouTubeDownloader(temp_dir, progress_hook)
                    
                    # 포맷 설정
                    is_audio_only = format_type in ["MP3 (음성만)", "M4A (고품질 음성)"]
                    quality_map = {
                        "128k (표준)": "128", "192k (고품질)": "192", "320k (최고품질)": "320"
                    }
                    video_quality_map = {
                        "360p (모바일)": "360", "480p (표준)": "480", "720p (HD)": "720", 
                        "1080p (풀HD)": "1080", "1440p (2K)": "1440", "2160p (4K)": "2160"
                    }
                    speed_map = {
                        "표준": "normal", "고속": "fast", "최고품질": "best"
                    }
                    filename_map = {
                        "자동": "auto", "간단": "simple", "상세": "detailed"
                    }
                    
                    progress_container = st.empty()
                    
                    if is_audio_only:
                        audio_quality = quality_map[quality]
                        format_ext = "m4a" if format_type == "M4A (고품질 음성)" else "mp3"
                        progress_container.info(f"🎵 {format_type} 다운로드 중... (최대 20분 소요)")
                        file_path = downloader.download_audio(url_input.strip(), audio_quality, playlist_option, format_ext)
                    else:
                        video_quality = video_quality_map[quality]
                        format_ext = "webm" if format_type == "WEBM (고효율 비디오)" else "mp4"
                        progress_container.info(f"🎬 {format_type} 다운로드 중... (최대 30분 소요)")
                        file_path = downloader.download_video(url_input.strip(), video_quality, playlist_option, format_ext)
                    
                    progress_container.empty()
                    
                    if file_path and os.path.exists(file_path):
                        # 파일명 정리
                        original_filename = os.path.basename(file_path)
                        safe_filename = sanitize_filename(original_filename)
                        
                        # 다운로드 링크 생성
                        download_link = create_download_link(file_path, safe_filename)
                        
                        if download_link:
                            st.success("다운로드가 완료되었습니다!")
                            st.markdown(download_link, unsafe_allow_html=True)
                            
                            # 파일 정보 표시
                            file_size = os.path.getsize(file_path)
                            file_ext = os.path.splitext(safe_filename)[1].upper()
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("파일 크기", format_bytes(file_size))
                            with col2:
                                st.metric("형식", file_ext[1:] if file_ext else "N/A")
                            with col3:
                                st.metric("품질", quality)
                            
                            # 다시 다운로드 버튼
                            if st.button("🔄 다른 형식으로 다운로드", use_container_width=True):
                                st.session_state.download_complete = False
                                st.rerun()
                        else:
                            st.error("다운로드 링크 생성에 실패했습니다.")
                    else:
                        st.error("다운로드에 실패했습니다. 다시 시도해주세요.")
                
                except Exception as e:
                    st.error(f"❌ 다운로드 중 오류가 발생했습니다: {str(e)}")
                
                finally:
                    # 임시 파일 정리
                    try:
                        shutil.rmtree(temp_dir, ignore_errors=True)
                    except:
                        pass
            else:
                st.error("❌ URL을 입력해주세요.")
    
    # 진행 상황 표시
    if st.session_state.download_progress > 0:
        st.progress(st.session_state.download_progress / 100)
        if st.session_state.download_status:
            st.info(st.session_state.download_status)
    
    # 푸터
    st.markdown("---")
    st.write("**개발자:** Sungwoo Cho (조성우)")
    st.caption("© 2025 Sungwoo Cho. 개인 및 교육용으로만 사용하세요.")

if __name__ == "__main__":
    main()
