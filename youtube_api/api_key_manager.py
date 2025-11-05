# youtube_api/api_key_manager.py
import random
import threading

class ApiKeyManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, api_keys: list = None):
        if not hasattr(self, 'initialized'):
            if not api_keys:
                raise ValueError("API 키 리스트는 비어있을 수 없습니다.")
            self.api_keys = api_keys
            self.initialized = True

    def get_next_key(self) -> str:
        """
        멀티프로세스 환경(Gunicorn)에서는 각 프로세스가 자신만의 인덱스를 가지므로
        순차적 순환보다 랜덤 선택이 키 사용량을 더 효과적으로 분산시킵니다.
        """
        return random.choice(self.api_keys)

# 싱글턴 인스턴스를 settings에서 초기화하여 사용
# from django.conf import settings
# api_key_manager = ApiKeyManager(settings.YOUTUBE_API_KEYS)
