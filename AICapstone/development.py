# AICapstone/AICapstone/development.py

from .base import *
from dotenv import load_dotenv
import os

load_dotenv()

# 개발 환경 설정
DEBUG = True

ALLOWED_HOSTS = []

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
