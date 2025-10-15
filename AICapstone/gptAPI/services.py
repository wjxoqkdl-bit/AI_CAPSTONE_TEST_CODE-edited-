# gptAPI/services.py
import openai
import json
import os
from django.conf import settings

def load_prompt_config():
    """prompts/keyword_extraction.json 파일에서 프롬프트 설정 로드"""
    config_path = os.path.join(settings.BASE_DIR, 'gptAPI', 'prompts', 'keyword_extraction.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading prompt config: {e}")
        return None

def extract_keywords(user_prompt: str, max_keywords: int = 5) -> list[str]:
    """사용자 프롬프트에서 GPT를 이용한 핵심 키워드 추출"""
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        print("Error: OpenAI API key is not configured.")
        return []

    prompt_config = load_prompt_config()
    if not prompt_config:
        return []

    openai.api_key = api_key

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
