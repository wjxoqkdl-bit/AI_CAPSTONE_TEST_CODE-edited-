from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List # 타입 힌트를 위해 추가

class YouTubeDataCollector:
    """
    YouTube API를 통해 크리에이터 ID 목록을 기반으로
    상세 데이터를 수집하는 역할을 합니다.
    """
    
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("API 키는 비어있을 수 없습니다.")
        self.youtube = build('youtube', 'v3', developerKey=api_key)

    def search_channels(self, keyword, max_results=5):
        """(보조 기능) 키워드로 채널을 검색하여 ID를 얻는 데 사용할 수 있습니다."""
        try:
            request = self.youtube.search().list(
                part="snippet", q=keyword, type="channel", maxResults=max_results
            )
            return request.execute().get("items", [])
        except HttpError as e:
            print(f"API 에러 (search_channels): {e}")
            return []

    def get_channel_details(self, channel_id):
        """채널 ID로 상세 정보를 가져옵니다."""
        try:
            request = self.youtube.channels().list(
                part="snippet,statistics,brandingSettings", id=channel_id
            )
            response = request.execute()
            return response.get("items", [{}])[0]
        except HttpError as e:
            print(f"API 에러 (get_channel_details): {e}")
            return None
    
    def get_latest_videos(self, channel_id, max_results=5):
        """채널 ID로 최신 동영상 목록을 가져옵니다."""
        try:
            request = self.youtube.search().list(
                part="snippet", channelId=channel_id, order="date", type="video", maxResults=max_results
            )
            return request.execute().get("items", [])
        except HttpError as e:
            print(f"API 에러 (get_latest_videos): {e}")
            return []

    def get_video_stats(self, video_ids: List[str]):
        """여러 동영상 ID의 상세 통계를 한 번에 가져옵니다."""
        try:
            request = self.youtube.videos().list(
                part="statistics,contentDetails", id=",".join(video_ids)
            )
            return request.execute().get("items", [])
        except HttpError as e:
            print(f"API 에러 (get_video_stats): {e}")
            return []
    
    # --- ✨ AI 연동을 위한 새로운 메인 함수 ✨ ---
    def get_creator_data_by_ids(self, channel_ids: List[str]):
        """
        크리에이터 ID 리스트를 입력받아, 각 크리에이터의 상세 정보와
        최신 영상 데이터를 종합하여 리스트 형태로 반환합니다.
        """
        print(f"{len(channel_ids)}명의 크리에이터에 대한 데이터 수집을 시작합니다...")
        
        collected_data = []
        for channel_id in channel_ids:
            print(f"-> 채널 ID: {channel_id} 데이터 수집 중...")
            
            # 1. 채널 기본 정보(프로필) 수집
            channel_profile = self.get_channel_details(channel_id)
            if not channel_profile:
                print(f"   - ID {channel_id}의 프로필을 가져올 수 없어 건너뜁니다.")
                continue

            # 2. 채널의 최신 영상 목록(스니펫) 가져오기
            latest_videos = self.get_latest_videos(channel_id)
            
            # 3. 최신 영상들의 통계 정보 한 번에 가져오기
            video_ids = [video['id']['videoId'] for video in latest_videos]
            if video_ids:
                video_stats = self.get_video_stats(video_ids)
            else:
                video_stats = []

            # 4. 수집된 데이터를 최종적으로 묶음
            collected_data.append({
                "channel_profile": channel_profile,
                "latest_videos": latest_videos,
                "video_stats": video_stats
            })
        
        print(f"총 {len(collected_data)}명의 크리에이터에 대한 데이터 수집을 완료했습니다.")
        return collected_data