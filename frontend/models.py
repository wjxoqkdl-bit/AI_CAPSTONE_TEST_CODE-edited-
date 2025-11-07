from django.db import models

# Create your models here.
# wjxoqkdl-bit/ai_capstone_test_code-edited-/AI_CAPSTONE_TEST_CODE-edited--b4f109e81c2e0339c6a3b49cd506a85a3bd5130c/frontend/models.py

from django.db import models
from django.contrib.auth.models import User  # (선택사항) 나중에 사용자별로 연동할 경우


class SearchHistory(models.Model):
    """
    사용자의 검색 기록을 저장하는 모델
    """
    # (선택사항) 나중에 로그인 기능과 연동 시
    # user = models.ForeignKey(User, on_delete=models.CASCADE)

    query = models.CharField(max_length=500, help_text="사용자가 입력한 원본 검색어")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="검색 시간")

    class Meta:
        ordering = ['-timestamp']  # 최신순으로 정렬
        verbose_name = "검색 기록"
        verbose_name_plural = "검색 기록"

    def __str__(self):
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M')}] {self.query}"