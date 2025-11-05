# youtube_api/api_key_manager.py
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
            self.current_index = 0
            self.lock = threading.Lock()
            self.initialized = True

    def get_next_key(self) -> str:
        with self.lock:
            key = self.api_keys[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            return key

# 싱글턴 인스턴스를 settings에서 초기화하여 사용
# from django.conf import settings
# api_key_manager = ApiKeyManager(settings.YOUTUBE_API_KEYS)
