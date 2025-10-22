# gptAPI/tests.py
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client

class GptAPITests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch('gptAPI.services.openai.chat.completions.create')
    def test_call_gpt_api_success(self, mock_openai_create):
        """API 성공 응답 시나리오 테스트"""
        # 모의 API가 반환할 JSON 형식의 문자열 설정
        mock_structured_response = {
            "subject": "테스트 주제",
            "modifiers": ["테스트 수식어"],
            "audience": "테스트 대상"
        }
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(mock_structured_response)
        mock_openai_create.return_value = mock_response

        # API에 테스트 요청 전송
        payload = {'prompt': 'Hello, AI!'}
        response = self.client.post(
            '/api/call/', 
            data=json.dumps(payload), 
            content_type='application/json'
        )

        # 응답 검증
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn('keywords', response_data)
        self.assertEqual(response_data['keywords'], mock_structured_response)

        # 외부 API 호출 횟수 검증
        mock_openai_create.assert_called_once()

    def test_call_gpt_api_no_prompt(self):
        """요청에 'prompt'가 없는 경우의 시나리오 테스트"""
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