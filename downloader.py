# Implement fallback strategies for video download to handle bot detection.
import yt_dlp
import os
import tempfile
import shutil
from pathlib import Path
import threading
import time
import random

class YouTubeDownloader:
    def __init__(self, output_dir, progress_hook=None):
        self.output_dir = output_dir
        self.progress_hook = progress_hook

    def get_base_ydl_opts(self, is_playlist=False):
        """기본 yt-dlp 옵션"""
        opts = {
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
            'noplaylist': not is_playlist,
            'extract_flat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'ignoreerrors': True,
            'no_warnings': False,
            'retries': 3,
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            # FFmpeg 자동 감지 (Streamlit Share 호환)
            'prefer_ffmpeg': True,
            # YouTube 봇 검증 우회 설정
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['configs', 'webpage']
                }
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }

        if self.progress_hook:
            opts['progress_hooks'] = [self.progress_hook]

        return opts

    def _get_android_opts(self, is_playlist):
        opts = self.get_base_ydl_opts(is_playlist)
        opts.update({
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Linux; Android 8.0.0; Pixel 2 XL Build/OPD1.171019.011) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
            },
            'source_address': '0.0.0.0'  # 필요한 경우 특정 IP 주소로 변경
        })
        return opts

    def _get_web_opts(self, is_playlist):
        opts = self.get_base_ydl_opts(is_playlist)
        opts.update({
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            },
            'source_address': '0.0.0.0'
        })
        return opts

    def _get_basic_opts(self, is_playlist):
        opts = self.get_base_ydl_opts(is_playlist)
        return opts

    def download_audio(self, url, quality="192", is_playlist=False, format_type="mp3"):
        """오디오 다운로드 (MP3, M4A 지원)"""
        ydl_opts = self.get_base_ydl_opts(is_playlist)

        if format_type == "m4a":
            ydl_opts.update({
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                    'preferredquality': quality,
                }],
            })
        else:
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': quality,
                }],
            })

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 단일 비디오 다운로드 (재생목록은 성능상 첫번째만)
                ydl.download([url])
                # 다운로드된 파일 찾기
                for file in os.listdir(self.output_dir):
                    if file.endswith(('.mp3', '.m4a')):
                        return os.path.join(self.output_dir, file)

        except Exception as e:
            raise Exception(f"오디오 다운로드 실패: {str(e)}")

        return None

    def download_video(self, url, quality="720", is_playlist=False, format_type="mp4"):
        """비디오 다운로드 (MP4, WEBM 지원)"""
        # 화질별 포맷 선택
        quality_formats = {
            "360": "best[height<=360]",
            "480": "best[height<=480]",
            "720": "best[height<=720]",
            "1080": "best[height<=1080]",
            "1440": "best[height<=1440]",
            "2160": "best[height<=2160]"
        }

        format_selector = quality_formats.get(quality, "best[height<=720]")

        # 여러 다운로드 전략 시도
        strategies = [
            self._get_android_opts,
            self._get_web_opts,
            self._get_basic_opts
        ]

        for strategy in strategies:
            try:
                ydl_opts = strategy(is_playlist)

                if format_type == "webm":
                    ydl_opts.update({
                        'format': f'{format_selector}[ext=webm]/best[ext=webm]/best',
                        'merge_output_format': 'webm',
                    })
                else:
                    ydl_opts.update({
                        'format': f'{format_selector}/best',
                        'merge_output_format': 'mp4',
                    })

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                    # 다운로드된 파일 찾기
                    for file in os.listdir(self.output_dir):
                        if file.endswith(('.mp4', '.webm', '.mkv')):
                            return os.path.join(self.output_dir, file)

            except Exception as e:
                if "Sign in to confirm" in str(e) and strategy != strategies[-1]:
                    time.sleep(random.uniform(2, 5))  # 랜덤 대기
                    continue
                elif strategy == strategies[-1]:
                    raise Exception(f"비디오 다운로드 실패: {str(e)}")

        return None

    def get_video_info(self, url):
        """비디오 정보 추출"""
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
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
