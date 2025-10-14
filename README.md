# AI 기반 유튜브 채널 추천 프로젝트

## 1. 프로젝트 개요

사용자가 자연어(장문)로 원하는 채널의 특징을 설명하면, AI가 핵심 키워드를 추출하고, 이 키워드를 바탕으로 유튜브에서 가장 적합한 채널을 검색하여 추천하는 웹 애플리케이션입니다.

## 2. 핵심 기능

*   **자연어 처리:** 사용자의 긴 요청 문장을 이해하고 처리합니다.
*   **AI 키워드 추출:** OpenAI(GPT) API를 사용하여 사용자의 요청에서 핵심 키워드를 자동으로 추출합니다.
*   **유튜브 채널 검색:** 추출된 키워드를 바탕으로 YouTube Data API를 통해 관련 채널을 검색합니다.
*   **웹 인터페이스:** Django와 HTMX를 사용하여 검색 요청 및 결과 확인을 위한 동적인 웹 UI를 제공합니다.

## 3. 프로젝트 구조

*   `frontend`: 사용자의 요청을 받고 결과를 보여주는 UI 및 핵심 로직을 담당합니다.
*   `gptAPI`: OpenAI API를 호출하여 키워드를 추출하는 서비스를 제공합니다.
*   `youtube_api`: YouTube Data API를 호출하여 채널을 검색하는 서비스를 제공합니다.
*   `AICapstone/settings/`: `base.py`, `development.py`, `production.py`로 분리된 환경별 설정 파일을 관리합니다.

## 4. 설치 및 실행 방법

### 사전 요구사항
*   Python 3.11 이상
*   Git

### 설치 순서
1.  **프로젝트 복제**
    ```bash
    git clone <저장소_URL>
    cd <프로젝트_폴더>
    ```

2.  **가상환경 생성 및 활성화**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate
    ```

3.  **라이브러리 설치**
    ```bash
    pip install -r requirements.txt
    ```

4.  **환경 변수 설정**
    프로젝트 최상위 폴더에 `.env` 파일을 생성하고, 아래와 같이 본인의 API 키를 입력합니다.
    ```
    OPENAI_API_KEY=sk-xxxxxxxxxxxx
    YOUTUBE_API_KEY=AIzaSyyyyyyyyyyy
    ```

5.  **데이터베이스 초기화 (최초 실행 시)**
    ```bash
    python manage.py migrate
    ```

6.  **개발 서버 실행**
    ```bash
    # 개발용 설정으로 서버를 실행합니다.
    python manage.py runserver
    ```
    서버 실행 후, 웹 브라우저에서 `http://127.0.0.1:8000/` 주소로 접속합니다.

## 5. 테스트 방법

프로젝트의 안정성을 확인하기 위해 아래 명령어로 테스트를 실행할 수 있습니다.

```bash
python manage.py test
```