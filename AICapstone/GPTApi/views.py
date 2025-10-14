from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import openai

# settings.py에서 API 키 설정
# 이 방식은 키가 코드 저장소에 직접 노출될 수 있으므로, 실제 프로덕션 환경에서는
# 환경 변수나 다른 보안 관리 도구를 사용하는 것이 더 안전합니다.
openai.api_key = getattr(settings, 'OPENAI_API_KEY', None)

@csrf_exempt  # 간단한 API 테스트를 위해 CSRF 보호를 비활성화합니다. 실제 서비스에서는 적절한 인증 방법을 사용해야 합니다.
def call_gpt_api(request):
    """
    GPT 모델을 호출하여 응답을 반환하는 API 뷰
    """
    if not openai.api_key:
        return JsonResponse({'error': 'OpenAI API key is not configured.'}, status=500, json_dumps_params={'ensure_ascii': False})

    if request.method == 'POST':
        try:
            # 요청 본문에서 JSON 데이터 파싱
            data = json.loads(request.body)
            prompt = data.get('prompt')

            if not prompt:
                return JsonResponse({'error': 'Prompt is required.'}, status=400, json_dumps_params={'ensure_ascii': False})

            # OpenAI API 호출
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",  # 필요에 따라 다른 모델 사용 가능
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024
            )

            # API 응답에서 텍스트 추출
            ai_response = response.choices[0].message.content.strip()

            return JsonResponse({'response': ai_response}, json_dumps_params={'ensure_ascii': False})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400, json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            # API 호출 중 발생할 수 있는 모든 예외 처리
            return JsonResponse({'error': str(e)}, status=500, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({'error': 'Only POST method is allowed.'}, status=405, json_dumps_params={'ensure_ascii': False})