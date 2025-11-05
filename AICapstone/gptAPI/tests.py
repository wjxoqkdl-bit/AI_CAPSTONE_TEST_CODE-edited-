from unittest.mock import patch
from django.test import TestCase, Client
from django.contrib.auth.models import User

class RecommendationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        # 테스트용 사용자 생성 및 강제 로그인
        self.test_user = User.objects.create_user(username='testuser', password='12345')
        self.client.force_login(self.test_user)

    @patch('frontend.views.YouTubeDataCollector')
    @patch('frontend.views.extract_keywords')
    def test_recommendation_view_success(self, mock_extract_keywords, mock_yt_collector):
        """추천 결과 뷰가 성공적으로 렌더링되는지 테스트"""
        # 1. 모의(Mock) 설정
        # extract_keywords가 검색어 리스트를 반환하도록 설정
        mock_extract_keywords.return_value = ["파이썬 기초", "코딩 입문"]

        # YouTubeDataCollector의 인스턴스 및 메소드 모킹
        mock_collector_instance = mock_yt_collector.return_value
        mock_collector_instance.search_channels.return_value = [
            {
                'id': {'channelId': 'test_channel_1'},
                'snippet': {
                    'title': 'Test Channel 1',
                    'description': 'Description 1',
                    'thumbnails': {'medium': {'url': 'http://example.com/thumb1.jpg'}}
                }
            }
        ]
        mock_collector_instance.get_channel_details.return_value = {
            'statistics': {'videoCount': '10', 'subscriberCount': '1000', 'viewCount': '100000'}
        }
        mock_collector_instance.get_latest_videos.return_value = [
            {
                'id': {'videoId': 'video1'},
                'snippet': {'publishedAt': '2023-01-01T00:00:00Z', 'title': 'Video 1', 'description': 'Desc 1', 'tags': ['tag1']}
            }
        ]
        mock_collector_instance.get_video_details.return_value = [
            {
                'statistics': {'likeCount': '100'},
                'contentDetails': {'duration': 'PT5M30S'},
                'snippet': {'title': 'Video 1', 'description': 'Desc 1', 'tags': ['tag1']}
            }
        ]

        # AI 분석/평가 함수 모킹 (단순 점수 반환)
        with patch('frontend.views.analyze_channel_texts') as mock_analyze, patch('frontend.views.rate_channel_relevance') as mock_rate:
            mock_analyze.return_value = "A great channel for beginners."
            mock_rate.return_value = {'score': 85, 'reason': 'Matches user query well.'}

            # 2. 테스트 요청
            response = self.client.post('/run-recommendation/', {'query': '파이썬 알려줘'})

            # 3. 검증
            self.assertEqual(response.status_code, 200)
            self.assertTemplateUsed(response, 'frontend/partials/_search_results.html')
            # response.context에서 result_data가 올바르게 채워졌는지 확인할 수 있습니다.
            self.assertIn('result_data', response.context)
            self.assertEqual(response.context['result_data']['user_query'], '파이썬 알려줘')
            self.assertTrue(len(response.context['result_data']['recommendations']) > 0)

    def test_recommendation_view_no_query(self):
        """쿼리 없이 요청 시 에러 메시지가 표시되는지 테스트"""
        response = self.client.post('/run-recommendation/', {'query': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/partials/_error.html')
        self.assertContains(response, "검색어를 입력해주세요.")