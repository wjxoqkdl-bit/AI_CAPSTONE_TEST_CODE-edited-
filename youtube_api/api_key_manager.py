# youtube_api/api_key_manager.py
import random
import threading

class ApiKeyManager:
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
        # Double-checked locking to ensure keys are loaded only once.
        if self.api_keys is None:
            with self.lock:
                if self.api_keys is None:
                    from django.conf import settings
                    keys = getattr(settings, 'YOUTUBE_API_KEYS', [])
                    if not keys:
                        raise ValueError("YOUTUBE_API_KEYS setting is missing or empty in Django settings.")
                    self.api_keys = keys

    def get_next_key(self) -> str:
        """
        Lazily loads keys on the first call and returns a random key.
        Random selection is better for distributing usage in a multi-process environment.
        """
        self._load_keys()
        return random.choice(self.api_keys)

# Create a single, global instance of the manager for the application to use.
api_key_manager = ApiKeyManager()
