# gptAPI/services.py
import openai
import json
import os
from django.conf import settings

def load_prompt_config():
    """JSON 파일에서 프롬프트 설정을 로드합니다."""
    # settings.BASE_DIR를 사용하여 프로젝트의 기본 경로를 기준으로 파일 경로를 구성합니다.
    # BASE_DIR는 .../AICapstone/ 입니다.
    config_path = os.path.join(settings.BASE_DIR, 'gptAPI', 'prompts', 'keyword_extraction.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Prompt config file not found at {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {config_path}")
        return None

def extract_keywords(user_prompt: str, max_keywords: int = 5) -> list[str]:
    """
    사용자의 긴 프롬프트에서 핵심 키워드를 추출합니다.
    (이제 JSON 파일에서 설정을 읽어옵니다)
    """
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        print("Error: OpenAI API key is not configured.")
        return []

    prompt_config = load_prompt_config()
    if not prompt_config:
        return []

    openai.api_key = api_key

    # JSON 설정에서 시스템 메시지를 가져와 포맷팅합니다.
    system_message = prompt_config['system_message'].format(max_keywords=max_keywords)

    try:
        response = openai.chat.completions.create(
            model=prompt_config['model'],
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=prompt_config['max_tokens'],
            temperature=prompt_config['temperature'],
        )

        keyword_string = response.choices[0].message.content.strip()
        keywords = [keyword.strip() for keyword in keyword_string.split(',') if keyword.strip()]
        return keywords

    except Exception as e:
        print(f"An error occurred during OpenAI API call: {e}")
        return []
