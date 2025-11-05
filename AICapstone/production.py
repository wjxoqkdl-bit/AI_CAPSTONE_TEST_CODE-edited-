# AICapstone/AICapstone/production.py

from .base import *

# 배포 환경 설정
DEBUG = False

# 실제 서비스할 도메인 및 Elastic Beanstalk 호스트를 이곳에 추가합니다.
ALLOWED_HOSTS = ['aicapstone-dev.ap-northeast-2.elasticbeanstalk.com', '.elasticbeanstalk.com', 'localhost', '127.0.0.1']

# static files
STATIC_ROOT = os.path.join(BASE_DIR.parent, 'staticfiles')


