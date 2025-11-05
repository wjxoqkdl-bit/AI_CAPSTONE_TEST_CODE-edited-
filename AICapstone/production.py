# AICapstone/AICapstone/production.py

from .base import *

# 배포 환경 설정
DEBUG = False

# 모든 호스트를 허용하여 502 오류의 원인이 ALLOWED_HOSTS인지 확인합니다.
ALLOWED_HOSTS = ['*']

# static files
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'staticfiles')


