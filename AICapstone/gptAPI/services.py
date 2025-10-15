# gptAPI/services.py
import openai
import json
import os
from django.conf import settings

def load_prompt_config(filename: str):
    """prompts 폴더에서 지정된 JSON 파일의 프롬프트 설정을 로드"""
    config_path = os.path.join(settings.BASE_DIR, 'gptAPI', 'prompts', filename)
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

    prompt_config = load_prompt_config('keyword_extraction.json')
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

def summarize_comments(comments: list[str]) -> str:
    """댓글 리스트를 GPT를 이용해 요약"""
    api_key = getattr(settings, 'OPENAI_API_KEY', None)
    if not api_key:
        print("Error: OpenAI API key is not configured.")
        return ""

    prompt_config = load_prompt_config('comment_summarization.json')
    if not prompt_config:
        return ""

    openai.api_key = api_key

    # 요약할 댓글들을 하나의 문자열로 합침
    comment_text = "\n".join(comments)
    user_content = f"Please summarize the following comments:\n\n{comment_text}"

    try:
        response = openai.chat.completions.create(
            model=prompt_config['model'],
            messages=[
                {"role": "system", "content": prompt_config['system_message']},
                {"role": "user", "content": user_content}
            ],
            max_tokens=prompt_config['max_tokens'],
            temperature=prompt_config['temperature'],
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"An error occurred during OpenAI API call: {e}")
        return ""
