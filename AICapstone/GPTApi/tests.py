# gptAPI/tests.py
import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client

class GptAPITests(TestCase):
    def setUp(self):
        # 모든 테스트 전에 클라이언트를 설정합니다.
        self.client = Client()

    @patch('gptAPI.views.openai.chat.completions.create')
    def test_call_gpt_api_success(self, mock_openai_create):
        """API 호출이 성공했을 때의 시나리오를 테스트합니다."""
        # 1. 모의(mock) API 응답 설정
        # 실제 OpenAI API 응답과 유사한 구조의 객체를 만듭니다.
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "This is a mock AI response."
        mock_openai_create.return_value = mock_response

        # 2. 테스트할 API에 POST 요청 보내기
        payload = {'prompt': 'Hello, AI!'}
        response = self.client.post(
            '/api/call/', 
            data=json.dumps(payload), 
            content_type='application/json'
        )

        # 3. 응답 검증
        # 응답 코드가 200 (성공)인지 확인합니다.
        self.assertEqual(response.status_code, 200)

        # 응답 JSON 데이터가 예상대로인지 확인합니다.
        response_data = response.json()
        self.assertIn('response', response_data)
        self.assertEqual(response_data['response'], "This is a mock AI response.")

        # 4. 외부 API가 정확히 한 번 호출되었는지 확인
        mock_openai_create.assert_called_once()

    def test_call_gpt_api_no_prompt(self):
        """요청에 'prompt'가 없을 때의 시나리오를 테스트합니다."""
        # 'prompt'가 없는 잘못된 요청 보내기
        payload = {'wrong_key': 'some_value'}
        response = self.client.post(
            '/api/call/', 
            data=json.dumps(payload), 
            content_type='application/json'
        )

        # 응답 코드가 400 (잘못된 요청)인지 확인합니다.
        self.assertEqual(response.status_code, 400)

        # 에러 메시지가 올바른지 확인합니다.
        response_data = response.json()
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Prompt is required.')