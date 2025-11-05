from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List
from django.conf import settings
from .api_key_manager import ApiKeyManager

# Initialize the ApiKeyManager as a singleton instance
if settings.YOUTUBE_API_KEYS:
    api_key_manager = ApiKeyManager(settings.YOUTUBE_API_KEYS)
else:
    api_key_manager = None

class YouTubeDataCollector:
    """YouTube Data API v3를 사용한 채널 및 비디오 데이터 수집"""
    
    def _get_youtube_service(self):
        if not api_key_manager:
            raise ValueError("API 키가 설정되지 않았습니다.")
        api_key = api_key_manager.get_next_key()
        return build('youtube', 'v3', developerKey=api_key)

    def search_channels(self, keyword, max_results=5):
        """키워드로 채널 검색"""
        try:
            youtube = self._get_youtube_service()
            request = youtube.search().list(
                part="snippet", q=keyword, type="channel", maxResults=max_results
            )
            return request.execute().get("items", [])
        except HttpError as e:
            print(f"API Error (search_channels): {e}")
            # 여기서 키 순환을 위해 재시도 로직을 추가할 수도 있습니다.
            return []

    def get_channel_details(self, channel_id):
        """채널 ID로 상세 정보 조회"""
        try:
            youtube = self._get_youtube_service()
            request = youtube.channels().list(
                part="snippet,statistics,brandingSettings", id=channel_id
            )
            response = request.execute()
            return response.get("items", [{}])[0]
        except HttpError as e:
            print(f"API Error (get_channel_details): {e}")
            return None
    
    def get_latest_videos(self, channel_id, max_results=5):
        """채널 ID로 최신 비디오 목록 조회"""
        try:
            youtube = self._get_youtube_service()
            request = youtube.search().list(
                part="snippet", channelId=channel_id, order="date", type="video", maxResults=max_results
            )
            return request.execute().get("items", [])
        except HttpError as e:
            print(f"API Error (get_latest_videos): {e}")
            return []

    def get_video_stats(self, video_ids: List[str]):
        """비디오 ID 목록으로 상세 통계 조회"""
        try:
            youtube = self._get_youtube_service()
            request = youtube.videos().list(
                part="statistics,contentDetails", id=",".join(video_ids)
            )
            return request.execute().get("items", [])
        except HttpError as e:
            print(f"API Error (get_video_stats): {e}")
            return []

    def get_video_details(self, video_ids: List[str]):
        """비디오 ID 목록으로 각 비디오의 상세 정보(제목, 설명, 태그, 통계) 조회"""
        try:
            youtube = self._get_youtube_service()
            request = youtube.videos().list(
                part="snippet,statistics", id=",".join(video_ids)
            )
            return request.execute().get("items", [])
        except HttpError as e:
            print(f"API Error (get_video_details): {e}")
            return []

    def get_video_comments(self, video_id: str, max_results=10):
        """비디오 ID로 댓글(상위 댓글만) 수집"""
        try:
            youtube = self._get_youtube_service()
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results,
                order="relevance"  # 관련성 높은 순
            )
            response = request.execute()
            return response.get("items", [])
        except HttpError as e:
            # 댓글이 비활성화된 경우 등 오류 발생 시 빈 리스트 반환
            print(f"API Error (get_video_comments): {e}")
            return []