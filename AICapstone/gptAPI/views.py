from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .services import extract_keywords

@csrf_exempt
def call_gpt_api(request):
    """
    사용자 프롬프트에서 키워드를 추출하여 반환하는 API 뷰입니다.
    (이제 services.py의 함수를 사용합니다)
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            prompt = data.get('prompt')

            if not prompt:
                return JsonResponse({'error': 'Prompt is required.'}, status=400, json_dumps_params={'ensure_ascii': False})

            # 서비스 함수를 호출하여 키워드 추출
            keywords = extract_keywords(prompt)

            if not keywords:
                return JsonResponse({'error': 'Failed to extract keywords.'}, status=500, json_dumps_params={'ensure_ascii': False})

            return JsonResponse({'keywords': keywords}, json_dumps_params={'ensure_ascii': False})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400, json_dumps_params={'ensure_ascii': False})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500, json_dumps_params={'ensure_ascii': False})

    return JsonResponse({'error': 'Only POST method is allowed.'}, status=405, json_dumps_params={'ensure_ascii': False})