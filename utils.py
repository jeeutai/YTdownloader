import re
import os
import yt_dlp

def sanitize_filename(filename):
    """파일명에서 특수문자 제거 및 정리"""
    # 확장자 분리
    name, ext = os.path.splitext(filename)
    
    # 특수문자 제거 및 공백 정리
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    
    # 길이 제한 (최대 100자)
    if len(name) > 100:
        name = name[:100]
    
    return name + ext

def validate_youtube_url(url):
    """YouTube URL 유효성 검증"""
    youtube_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+',
        r'https?://(?:www\.)?youtube\.com/playlist\?list=[\w-]+',
        r'https?://youtu\.be/[\w-]+',
        r'https?://(?:www\.)?youtube\.com/embed/[\w-]+',
        r'https?://(?:m\.)?youtube\.com/watch\?v=[\w-]+',
    ]
    
    for pattern in youtube_patterns:
        if re.match(pattern, url.strip()):
            return True
    
    return False

def format_bytes(bytes_value):
    """바이트를 사람이 읽기 쉬운 형태로 변환"""
    if bytes_value == 0:
        return "0 B"
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    unit_index = 0
    
    while bytes_value >= 1024 and unit_index < len(units) - 1:
        bytes_value /= 1024
        unit_index += 1
    
    return f"{bytes_value:.1f} {units[unit_index]}"

def get_video_info(url):
    """비디오 정보 가져오기"""
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        # YouTube 봇 검증 우회 설정
        'extractor_args': {
            'youtube': {
                'skip': ['dash', 'hls'],
                'player_skip': ['configs', 'webpage']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info:
                # 재생목록인지 확인
                is_playlist = 'entries' in info and len(info.get('entries', [])) > 1
                
                if is_playlist:
                    # 재생목록 정보
                    entries = [entry for entry in info['entries'] if entry]
                    first_video = entries[0] if entries else {}
                    
                    return {
                        'title': info.get('title', first_video.get('title', 'Unknown')),
                        'uploader': info.get('uploader', first_video.get('uploader', 'Unknown')),
                        'view_count': first_video.get('view_count', 0),
                        'duration_string': first_video.get('duration_string', 'N/A'),
                        'thumbnail': first_video.get('thumbnail'),
                        'playlist_count': len(entries),
                        'is_playlist': True
                    }
                else:
                    # 단일 비디오 정보
                    return {
                        'title': info.get('title', 'Unknown'),
                        'uploader': info.get('uploader', 'Unknown'),
                        'view_count': info.get('view_count', 0),
                        'duration_string': info.get('duration_string', 'N/A'),
                        'thumbnail': info.get('thumbnail'),
                        'playlist_count': None,
                        'is_playlist': False
                    }
                
    except Exception as e:
        return None

def format_duration(seconds):
    """초를 시:분:초 형태로 변환"""
    if not seconds:
        return "N/A"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def clean_title(title):
    """비디오 제목 정리"""
    if not title:
        return "Unknown Title"
    
    # HTML 엔터티 디코딩
    title = title.replace('&amp;', '&')
    title = title.replace('&lt;', '<')
    title = title.replace('&gt;', '>')
    title = title.replace('&quot;', '"')
    title = title.replace('&#39;', "'")
    
    # 길이 제한
    if len(title) > 80:
        title = title[:77] + "..."
    
    return title
