# frontend/views.py

import random
import time
from django.shortcuts import render

# 사용자의 웹 요청을 처리하는 함수들의 모음

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
    "AI 추천 결과 (HTMX가 이 부분을 로드)"
    user_query = request.POST.get('query', '요청하신 내용')
    time.sleep(1) # AI가 분석하는 것처럼 보이기 위한 딜레이

    # 3가지 시나리오의 임시 데이터
    tech_result = {
        'summary': f'"{user_query}" 관련 특징 분석 결과입니다.',
        'analysis_table': [{'category': '주제', 'value': '최신 스마트폰, 게이밍 기어', 'score': 0.96},
                           {'category': '분위기', 'value': '유머러스, 빠른 템포', 'score': 0.91}],
        'recommendation_summary': '분석 결과를 바탕으로 다음 채널들을 추천합니다.',
        'recommendations': ['ITSub', 'TechFunny', 'Gadget Pro']
    }
    cooking_result = {
        'summary': f'"{user_query}" 요청에 대해, 맛있는 인생을 선사하는 채널들을 찾았습니다.',
        'analysis_table': [{'category': '주제', 'value': '홈베이킹, 한식, 간단한 요리', 'score': 0.98},
                           {'category': '분위기', 'value': '차분한, ASMR, 갬성있는 영상', 'score': 0.95}],
        'recommendation_summary': '이런 분위기를 좋아하신다면, 아래 채널들을 확인해 보세요.',
        'recommendations': ['Peaceful Kitchen', 'Suna\'s Home Cafe']
    }
    kids_result = {
        'summary': f'"{user_query}"와 같은 아이들을 위한 채널의 특징은 다음과 같습니다.',
        'analysis_table': [{'category': '주제', 'value': '알파벳 놀이, 숫자 공부, 과학 실험', 'score': 0.97},
                           {'category': '분위기', 'value': '밝고 활기참, 다채로운 색감', 'score': 0.93}],
        'recommendation_summary': '아이와 함께 시청하기 좋은 채널들을 추천해 드립니다.',
        'recommendations': ['Little Baby Bum', 'Cocomelon']
    }

    # 3가지 결과 중 하나를 무작위로 선택.
    selected_data = random.choice([tech_result, cooking_result, kids_result])

    context = {'recommendation_data': selected_data}
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