import random
import threading

class ApiKeyManager:
    """
    Django settings에서 API 키를 로드하고 관리하는 싱글톤 클래스.
    get_next_key()는 무작위 키를 반환하여 부하를 분산시킵니다.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            # Initialize with None. Keys will be loaded on first use.
            self.api_keys = None
            self.lock = threading.Lock()
            self.initialized = True

    def _load_keys(self):
        """
        [핵심] Django settings에서 키를 단 한 번만 로드하는 메서드.
        스레드 세이프(Thread-safe)하게 처리됩니다.
        """
        # Double-checked locking
        if self.api_keys is None:
            with self.lock:
                if self.api_keys is None:
                    try:
                        from django.conf import settings
                        keys = getattr(settings, 'YOUTUBE_API_KEYS', [])
                        if not keys:
                            raise ValueError("YOUTUBE_API_KEYS setting is missing or empty in Django settings.")
                        self.api_keys = keys
                        print(f"ApiKeyManager: {len(self.api_keys)}개의 키를 Django settings에서 로드했습니다.")
                    except ImportError:
                        raise ImportError("ApiKeyManager는 Django 환경 외부에서 사용될 수 없습니다. (django.conf.settings를 찾을 수 없음)")

    def get_next_key(self) -> str:
        """
        무작위 키를 반환합니다.
        (참고: 이 메서드를 호출하면 내부적으로 _load_keys()가 트리거됩니다.)
        """
        self._load_keys() 
        return random.choice(self.api_keys)
    
    def get_all_keys(self) -> list:
        """
        [신규 추가] 순차적 키 로테이션을 위해 모든 키 목록을 반환합니다.
        """
        self._load_keys()
        return list(self.api_keys) # 사본 반환

# Create a single, global instance of the manager for the application to use.
api_key_manager = ApiKeyManager()