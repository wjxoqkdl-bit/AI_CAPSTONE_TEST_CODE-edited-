from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List

class YouTubeDataCollector:
    """YouTube Data API v3를 사용한 채널 및 비디오 데이터 수집"""
    
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API 키는 비어있을 수 없습니다.")
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def search_channels(self, keyword, max_results=5):
        """키워드로 채널 검색"""
        try:
            request = self.youtube.search().list(
                part="snippet", q=keyword, type="channel", maxResults=max_results
            )
            return request.execute().get("items", [])
        except HttpError as e:
            print(f"API Error (search_channels): {e}")
            return []

    def get_channel_details(self, channel_id):
        """채널 ID로 상세 정보 조회"""
        try:
            request = self.youtube.channels().list(
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
            request = self.youtube.search().list(
                part="snippet", channelId=channel_id, order="date", type="video", maxResults=max_results
            )
            return request.execute().get("items", [])
        except HttpError as e:
            print(f"API Error (get_latest_videos): {e}")
            return []

    def get_video_stats(self, video_ids: List[str]):
        """비디오 ID 목록으로 상세 통계 조회"""
        try:
            request = self.youtube.videos().list(
                part="statistics,contentDetails", id=",".join(video_ids)
            )
            return request.execute().get("items", [])
        except HttpError as e:
            print(f"API Error (get_video_stats): {e}")
            return []
    
    def get_creator_data_by_ids(self, channel_ids: List[str]):
        """채널 ID 리스트로 각 채널의 상세 정보와 최신 비디오 데이터 종합 반환"""
        collected_data = []
        for channel_id in channel_ids:
            channel_profile = self.get_channel_details(channel_id)
            if not channel_profile:
                continue

            latest_videos = self.get_latest_videos(channel_id)
            
            video_ids = [video['id']['videoId'] for video in latest_videos]
            if video_ids:
                video_stats = self.get_video_stats(video_ids)
            else:
                video_stats = []

            collected_data.append({
                "channel_profile": channel_profile,
                "latest_videos": latest_videos,
                "video_stats": video_stats
            })
        
        return collected_data