# frontend/views.py

from django.shortcuts import render
from django.conf import settings

# 다른 앱의 서비스와 클래스를 가져옵니다.
from gptAPI.services import extract_keywords
from youtube_api.api_client import YouTubeDataCollector

def login_view(request):
    "로그인 페이지"
    return render(request, 'frontend/login.html')


def search_page_view(request):
    "메인 검색 페이지"
    dummy_chat_list = [
        {'id': 1, 'title': '20대 타겟 IT 채널 추천'},
        {'id': 2, 'title': '힐링되는 요리 브이로그'},
        {'id': 3, 'title': '어린이용 과학 콘텐츠'},
    ]
    dummy_quick_history = [
        '10대 타겟 뷰티 채널', '요리 브이로그, 차분한 분위기', '30대 여성을 위한 재테크 정보'
    ]
    context = {'chat_list': dummy_chat_list, 'quick_history': dummy_quick_history}
    return render(request, 'frontend/search.html', context)


def recommendation_result_view(request):
    """AI 추천 결과를 실제 API를 호출하여 처리합니다."""
    user_query = request.POST.get('query', '')
    if not user_query:
        # 간단한 에러 처리, 실제로는 더 정교한 처리가 필요할 수 있습니다.
        context = {'recommendation_data': {'summary': '검색어를 입력해주세요.'}}
        return render(request, 'frontend/partials/_search_results.html', context)

    # 1. gptAPI 서비스를 호출하여 키워드 추출
    keywords = extract_keywords(user_query)
    if not keywords:
        context = {'recommendation_data': {'summary': '입력하신 내용에서 키워드를 추출하지 못했습니다.'}}
        return render(request, 'frontend/partials/_search_results.html', context)

    # 2. youtube_api 서비스를 호출하여 채널 검색 (가장 첫 키워드 사용)
    youtube_api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    if not youtube_api_key:
        context = {'recommendation_data': {'summary': 'YOUTUBE_API_KEY가 설정되지 않았습니다.'}}
        return render(request, 'frontend/partials/_search_results.html', context)

    collector = YouTubeDataCollector(youtube_api_key)
    # 여러 키워드 중 첫 번째 키워드를 검색에 사용
    search_keyword = keywords[0]
    found_channels = collector.search_channels(keyword=search_keyword, max_results=5)

    # 3. 검색 결과를 템플릿에 맞는 형식으로 가공
    recommendations = []
    for channel in found_channels:
        recommendations.append(channel['snippet']['title'])

    # 템플릿에 전달할 최종 데이터
    result_data = {
        'summary': f'\"{user_query}\" 요청에 대한 분석 결과입니다.',
        'analysis_table': [
            {'category': '핵심 키워드', 'value': ", ".join(keywords), 'score': 0.95},
            {'category': '검색 키워드', 'value': search_keyword, 'score': 0.90}
        ],
        'recommendation_summary': f'\'{search_keyword}\'(으)로 검색한 결과, 다음과 같은 채널을 추천합니다.',
        'recommendations': recommendations if recommendations else ['추천 채널을 찾지 못했습니다.']
    }

    context = {'recommendation_data': result_data}
    return render(request, 'frontend/partials/_search_results.html', context)


def load_chat_view(request, chat_id):
    "과거 채팅 기록 로드 (HTMX가 이 부분을 로드)"
    past_data = {
        'summary': f'**{chat_id}번 추천 기록**을 다시 보여드립니다. 당시의 분석 결과 요약입니다.',
        'analysis_table': [
            {'category': '과거 요청 주제', 'value': '20대 타겟 IT 채널 추천', 'score': 0.90},
        ],
        'recommendation_summary': '이 분석을 바탕으로 당시 추천드렸던 채널은 다음과 같습니다.',
        'recommendations': ['과거 추천 채널 1', '과거 추천 채널 2']
    }
    context = {'recommendation_data': past_data}
    return render(request, 'frontend/partials/_search_results.html', context)