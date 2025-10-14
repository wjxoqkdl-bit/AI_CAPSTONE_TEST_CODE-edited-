# gptAPI/tests.py
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client

class GptAPITests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('gptAPI.services.openai.chat.completions.create')
    def test_call_gpt_api_success(self, mock_openai_create):
        """API 호출이 성공했을 때의 시나리오를 테스트합니다."""
        # 1. 모의 API가 반환할 값을 설정합니다.
        # 실제 키워드 추출 결과와 유사하게 쉼표로 구분된 문자열을 반환하도록 설정합니다.
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "keyword1, keyword2, keyword3"
        mock_openai_create.return_value = mock_response

        # 2. 테스트할 API에 POST 요청을 보냅니다.
        payload = {'prompt': 'Hello, AI!'}
        response = self.client.post(
            '/api/call/', 
            data=json.dumps(payload), 
            content_type='application/json'
        )

        # 3. 응답을 검증합니다.
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        # 이제 API는 'keywords' 리스트를 반환하므로, 그것을 확인합니다.
        self.assertIn('keywords', response_data)
        self.assertEqual(response_data['keywords'], ["keyword1", "keyword2", "keyword3"])

        # 4. 외부 API가 정확히 한 번 호출되었는지 확인합니다.
        mock_openai_create.assert_called_once()

    def test_call_gpt_api_no_prompt(self):
        """요청에 'prompt'가 없을 때의 시나리오를 테스트합니다."""
        payload = {'wrong_key': 'some_value'}
        response = self.client.post(
            '/api/call/', 
            data=json.dumps(payload), 
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Prompt is required.')