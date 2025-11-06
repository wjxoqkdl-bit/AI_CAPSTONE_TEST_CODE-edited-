from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Callable, Any
import time

# [수정] ApiKeyManager의 전역 인스턴스를 임포트합니다.
from .api_key_manager import api_key_manager 

class YouTubeDataCollector:
    """
    YouTube Data API v3를 사용한 채널 및 비디오 데이터 수집
    (ApiKeyManager에서 키를 받아와 순차적으로 로테이션)
    """
    
    def __init__(self):
        """
        [수정]
        ApiKeyManager로부터 키 목록 전체를 받아와 내부적으로 관리합니다.
        더 이상 api_keys 리스트를 인자로 받지 않습니다.
        """
        
        # 1. 중앙 관리자로부터 모든 키 목록을 가져옵니다.
        #    (get_all_keys가 내부적으로 _load_keys()를 호출하여 키를 로드합니다)
        try:
            self.api_keys = api_key_manager.get_all_keys() 
        except (ValueError, ImportError) as e:
            print(f"ApiKeyManager에서 키를 로드하는 중 심각한 오류 발생: {e}")
            # Django settings에 키가 없으면 클래스 사용이 불가능하므로 에러를 다시 발생시킴
            raise
        
        if not self.api_keys:
             # 이 경우는 get_all_keys() 내부에서 이미 오류를 발생시키지만, 추가 방어 코드
             raise ValueError("API keys must be a non-empty list of strings.")
            
        self.current_key_index = 0
        
        # [수정] 첫 번째 키로 YouTube 서비스 객체 빌드
        self.youtube = self._build_service(self.api_keys[self.current_key_index])
        print(f"YouTubeDataCollector: ApiKeyManager로부터 {len(self.api_keys)}개의 키를 로드했습니다. Key #{self.current_key_index + 1}로 시작합니다.")

    def _build_service(self, api_key: str):
        """[기존과 동일] 현재 API 키로 YouTube 서비스 객체를 빌드합니다."""
        return build('youtube', 'v3', developerKey=api_key)

    def _switch_key(self):
        """[기존과 동일] 다음 API 키로 순차적으로 전환합니다."""
        self.current_key_index += 1
        if self.current_key_index >= len(self.api_keys):
            # 모든 키가 소진됨
            raise RuntimeError("모든 YouTube API 키의 할당량이 소진되었습니다.")
        
        print(f"알림: API 키 할당량 문제 발생. Key #{self.current_key_index + 1}로 전환합니다...")
        # 새 키로 서비스 객체를 다시 빌드
        self.youtube = self._build_service(self.api_keys[self.current_key_index])

    def _execute_request(self, request_builder: Callable[..., Any]):
        """
        [기존과 동일] 요청을 실행하고, 403(할당량) 오류 시 키를 전환하며 재시도합니다.
        """
        while True:
            try:
                # 1. 현재 youtube 서비스 객체로 요청(request)을 생성하고 실행
                request = request_builder(self.youtube)
                return request.execute()
            
            except HttpError as e:
                # 2. 403 오류는 일반적으로 할당량 문제 또는 권한 문제
                if e.resp.status == 403:
                    print(f"API Key #{self.current_key_index + 1} (403 Error: {e}).")
                    try:
                        # 3. 다음 키로 순차적 전환 시도
                        self._switch_key()
                        # 4. 키 전환 성공 시, 루프의 처음으로 돌아가 요청 재시도
                        continue 
                    except RuntimeError as re:
                        # 5. _switch_key()에서 오류 발생 (모든 키 소진)
                        print(re) # "모든... 키가... 소진되었습니다."
                        raise e # 마지막 HttpError를 다시 발생시킴
                else:
                    # 6. 403이 아닌 다른 오류 (예: 404, 400)는 재시도하지 않음
                    print(f"API Error (Non-403): {e}")
                    raise e

    # --- (이하 모든 메서드는 수정할 필요 없이 기존과 동일) ---

    def search_channels(self, keyword, max_results=5):
        """키워드로 채널 검색"""
        try:
            def builder(youtube_service):
                return youtube_service.search().list(
                    part="snippet", q=keyword, type="channel", maxResults=max_results
                )
            
            response = self._execute_request(builder)
            return response.get("items", [])
        
        except HttpError as e:
            print(f"API Error (search_channels) after all retries: {e}")
            return []

    def get_channel_details(self, channel_id):
        """채널 ID로 상세 정보 조회"""
        try:
            def builder(youtube_service):
                return youtube_service.channels().list(
                    part="snippet,statistics,brandingSettings,contentDetails", 
                    id=channel_id
                )
            
            response = self._execute_request(builder)
            return response.get("items", [{}])[0]
        
        except HttpError as e:
            print(f"API Error (get_channel_details) after all retries: {e}")
            return None
    
    def get_latest_videos(self, channel_id, max_results=5):
        """채널 ID로 최신 비디오 목록 조회 (할당량 최적화)"""
        try:
            # 첫 번째 API 호출 (채널 정보 조회)
            def channel_builder(youtube_service):
                return youtube_service.channels().list(
                    part="contentDetails", 
                    id=channel_id
                )
            channels_response = self._execute_request(channel_builder)
            
            uploads_playlist_id = channels_response.get("items", [{}])[0] \
                                                .get("contentDetails", {}) \
                                                .get("relatedPlaylists", {}) \
                                                .get("uploads")
            
            if not uploads_playlist_id:
                print(f"Error: '{channel_id}'의 업로드 재생목록을 찾을 수 없습니다.")
                return []

            # 두 번째 API 호출 (재생목록 아이템 조회)
            def items_builder(youtube_service):
                return youtube_service.playlistItems().list(
                    part="snippet",
                    playlistId=uploads_playlist_id,
                    maxResults=max_results
                )
            
            response = self._execute_request(items_builder)
            return response.get("items", [])
        
        except HttpError as e:
            print(f"API Error (get_latest_videos) after all retries: {e}")
            return []

    def get_video_details(self, video_ids: List[str]):
        """비디오 ID 목록으로 상세 정보 조회 (배칭 처리)"""
        all_items = []
        try:
            for i in range(0, len(video_ids), 50):
                chunk = video_ids[i:i+50]
                
                def builder(youtube_service):
                    return youtube_service.videos().list(
                        part="snippet,statistics,contentDetails",
                        id=",".join(chunk)
                    )
                
                response = self._execute_request(builder)
                all_items.extend(response.get("items", []))
            
            return all_items
        
        except HttpError as e:
            print(f"API Error (get_video_details) after all retries: {e}")
            return all_items

    def get_video_comments(self, video_id: str, max_results=100):
        """비디오 ID로 댓글 수집"""
        try:
            def builder(youtube_service):
                return youtube_service.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=max_results,
                    order="relevance"
                )
            
            response = self._execute_request(builder)
            return response.get("items", [])
        
        except HttpError as e:
            if 'commentsDisabled' in str(e):
                print(f"Info (get_video_comments): 비디오({video_id})의 댓글이 비활성화되었습니다.")
            else:
                 print(f"API Error (get_video_comments) after all retries: {e}")
            return []