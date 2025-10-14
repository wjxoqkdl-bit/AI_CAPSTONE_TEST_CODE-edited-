# gptAPI/services.py
import openai
from django.conf import settings

def extract_keywords(user_prompt: str, max_keywords: int = 5) -> list[str]:
    """
    사용자의 긴 프롬프트에서 핵심 키워드를 추출합니다.

    :param user_prompt: 사용자가 입력한 장문형 텍스트
    :param max_keywords: 추출할 최대 키워드 수
    :return: 추출된 키워드 리스트
    """
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        # 실제 프로덕션에서는 로깅 등으로 처리하는 것이 좋습니다.
        print("Error: OpenAI API key is not configured.")
        return []

    openai.api_key = api_key

    # 키워드 추출을 위한 시스템 메시지 정의
    system_message = f"""
    You are an expert at extracting the most relevant keywords from a user's request.
    Extract the top {max_keywords} most important keywords that represent the user's intent.
    The keywords should be suitable for a YouTube channel search.
    Return the keywords as a comma-separated list. For example: 'keyword1, keyword2, keyword3'
    Do not add any extra text, explanation, or formatting.
    """

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=50,  # 키워드 추출에는 많은 토큰이 필요하지 않습니다.
            temperature=0.2, # 키워드 추출은 일관성이 중요하므로 온도를 낮게 설정
        )

        # API 응답에서 키워드 텍스트 추출
        keyword_string = response.choices[0].message.content.strip()
        
        # 쉼표로 구분된 문자열을 리스트로 변환
        keywords = [keyword.strip() for keyword in keyword_string.split(',') if keyword.strip()]
        return keywords

    except Exception as e:
        print(f"An error occurred during OpenAI API call: {e}")
        return []
