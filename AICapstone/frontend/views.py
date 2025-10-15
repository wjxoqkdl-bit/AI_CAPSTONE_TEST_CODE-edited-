from django.shortcuts import render
from django.conf import settings

from gptAPI.services import extract_keywords, summarize_comments
from youtube_api.api_client import YouTubeDataCollector

def login_view(request):
    """로그인 페이지 렌더링"""
    return render(request, 'frontend/login.html')

def search_page_view(request):
    """메인 검색 페이지 렌더링 (더미 데이터 포함)"""
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
    """사용자 쿼리로 키워드 추출, 채널 검색, 댓글 요약을 거쳐 최종 채널 추천"""
    user_query = request.POST.get('query', '')
    if not user_query:
        return render(request, 'frontend/partials/_error.html', {'message': '검색어를 입력해주세요.'})

    # 1. 키워드 추출
    keywords = extract_keywords(user_query)
    if not keywords:
        return render(request, 'frontend/partials/_error.html', {'message': '입력하신 내용에서 키워드를 추출하지 못했습니다.'})

    # 2. 유튜브 채널 검색
    youtube_api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    if not youtube_api_key:
        return render(request, 'frontend/partials/_error.html', {'message': 'YOUTUBE_API_KEY가 설정되지 않았습니다.'})

    collector = YouTubeDataCollector(youtube_api_key)
    search_keyword = keywords[0]
    found_channels = collector.search_channels(keyword=search_keyword, max_results=3) # 후보군 3개로 제한

    # 3. 각 채널의 댓글 분석 및 최종 추천 데이터 생성
    channel_recommendations = []
    for channel in found_channels:
        channel_id = channel['id']['channelId']
        latest_videos = collector.get_latest_videos(channel_id, max_results=1)
        if not latest_videos:
            continue

        # 대표 영상 1개의 댓글 수집 및 요약
        video_id = latest_videos[0]['id']['videoId']
        comments_raw = collector.get_video_comments(video_id, max_results=50)
        comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in comments_raw]
        
        comment_summary = ""
        if comments:
            comment_summary = summarize_comments(comments)

        channel_info = {
            'title': channel['snippet']['title'],
            'description': channel['snippet']['description'],
            'thumbnail': channel['snippet']['thumbnails']['medium']['url'],
            'comment_summary': comment_summary or "댓글이 없거나 요약할 수 없습니다."
        }
        channel_recommendations.append(channel_info)

    # 4. 템플릿에 전달할 최종 데이터 가공
    result_data = {
        'user_query': user_query,
        'keywords': keywords,
        'recommendations': channel_recommendations
    }

    context = {'result_data': result_data}
    return render(request, 'frontend/partials/_search_results.html', context)

def load_chat_view(request, chat_id):
    """과거 채팅 기록 렌더링 (더미 데이터)"""
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

