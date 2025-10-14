# 2025_AI_Capstone

2025_AI_Capstone

# 메인 건들지 말것

python=3.11

## 기능 설명

### Youtube Data API 기능
API 기능 구현했습니다.
run_creator_search.py 코드에 채널 ID 넣으면 검색되게끔 구현했습니다.

*   `2025_AI_CAPSTONE/AICapstone/youtube_api/api_client.py` ➡️ api로 데이터 불러오는 코드
*   `2025_AI_CAPSTONE/AICapstone/run_creator_search.py` ➡️ 테스트 데이터 입력하는 코드
*   `2025_AI_CAPSTONE/AICapstone/HHS_requirements.txt` ➡️ 가상환경 라이브러리 설치
*   `2025_AI_CAPSTONE/AICapstone/.env` ➡️ API 입력

#### 테스트 방법
1.  `2025_AI_CAPSTONE/AICapstone` 경로로 이동
2.  `python -m venv venv` (가상환경 생성)
3.  `.\venv\Scripts\activate` (가상환경 활성화)
4.  `pip install -r ..\HHS_requirements.txt` (라이브러리 설치)
5.  `python run_creator_search.py` (실행)

### Streamlit 프론트엔드
*   **실행방법:** `streamlit run front_app.py`
*   **아이디:** `user1`
*   **비밀번호:** `pass1`
