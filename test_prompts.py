import os
import json
from dotenv import load_dotenv
import openai

# 1. .env 파일 로드
# 프로젝트 최상위 폴더에 있는 .env 파일을 로드합니다.
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# 2. API 키 설정
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if not OPENAI_API_KEY:
    print("Error: OPENAI_API_KEY is not set in the .env file.")
    exit()
openai.api_key = OPENAI_API_KEY

# 3. 프롬프트 설정 로드 함수 (gptAPI/services.py에서 가져옴)
def load_prompt_config(filename: str):
    """prompts 폴더에서 지정된 JSON 파일의 프롬프트 설정을 로드"""
    # 이 스크립트의 위치를 기준으로 gptAPI/prompts 경로를 찾습니다.
    script_dir = os.path.dirname(__file__)
    config_path = os.path.join(script_dir, 'AICapstone', 'gptAPI', 'prompts', filename)
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading prompt config from {config_path}: {e}")
        return None

# 4. 키워드 추출 함수 (gptAPI/services.py에서 가져옴)
def extract_keywords_standalone(user_prompt: str) -> dict:
    """사용자 프롬프트에서 구조화된 키워드(주제, 수식어, 대상)를 추출"""
    prompt_config = load_prompt_config('keyword_extraction.json')
    if not prompt_config:
        return {}

    try:
        response = openai.chat.completions.create(
            model=prompt_config['model'],
            messages=[
                {"role": "system", "content": prompt_config['system_message']},
                {"role": "user", "content": user_prompt}
            ],
            response_format=prompt_config.get('response_format'),
            max_tokens=prompt_config['max_tokens'],
            temperature=prompt_config['temperature'],
        )
        
        structured_keywords = json.loads(response.choices[0].message.content)
        return structured_keywords

    except Exception as e:
        print(f"An error occurred during OpenAI API call: {e}")
        return {}

# 5. 스크립트 실행 부분
if __name__ == "__main__":
    print("--- 프롬프트 엔지니어링 테스트 스크립트 ---")
    print("종료하려면 'exit' 또는 'quit'를 입력하세요.")

    while True:
        user_input = input("\n사용자 질문을 입력하세요: ")
        if user_input.lower() in ['exit', 'quit']:
            break

        if not user_input.strip():
            print("질문을 입력해주세요.")
            continue

        print("키워드 추출 중...")
        keywords = extract_keywords_standalone(user_input)

        if keywords:
            print("\n--- 추출된 키워드 ---" )
            print(f"주제: {keywords.get('subject', 'N/A')}")
            print(f"수식어: {keywords.get('modifiers', 'N/A')}")
            print(f"대상: {keywords.get('audience', 'N/A')}")
            print("---------------------")
        else:
            print("키워드 추출에 실패했습니다.")

    print("스크립트를 종료합니다.")
