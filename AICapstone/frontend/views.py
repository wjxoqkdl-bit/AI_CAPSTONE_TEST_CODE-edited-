from django.shortcuts import render
from django.conf import settings

from gptAPI.services import extract_keywords, summarize_comments, analyze_channel_texts, rate_channel_relevance
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
    """사용자 쿼리를 기반으로 AI 분석 및 평가를 거쳐 채널을 추천"""
    user_query = request.POST.get('query', '')
    if not user_query:
        return render(request, 'frontend/partials/_error.html', {'message': '검색어를 입력해주세요.'})

    structured_keywords = extract_keywords(user_query)
    if not structured_keywords or not structured_keywords.get('subject'):
        return render(request, 'frontend/partials/_error.html', {'message': '키워드를 추출하지 못했습니다.'})

    youtube_api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    if not youtube_api_key:
        return render(request, 'frontend/partials/_error.html', {'message': 'YOUTUBE_API_KEY가 설정되지 않았습니다.'})

    # 핵심 '주제' 키워드만으로 검색 쿼리 생성
    search_query = structured_keywords.get('subject', '')

    collector = YouTubeDataCollector(youtube_api_key)
    # 더 많은 후보군을 확보하기 위해 검색 결과 수를 늘림
    found_channels = collector.search_channels(keyword=search_query, max_results=10)

    rated_channels = []
    for channel in found_channels:
        channel_id = channel['id']['channelId']
        channel_title = channel['snippet']['title']
        channel_description = channel['snippet']['description']

        latest_videos = collector.get_latest_videos(channel_id, max_results=3)
        video_ids = [video['id']['videoId'] for video in latest_videos]
        video_details = collector.get_video_details(video_ids)

        all_texts = [channel_title, channel_description]
        for detail in video_details:
            snippet = detail.get('snippet', {})
            all_texts.append(snippet.get('title', ''))
            all_texts.append(snippet.get('description', ''))
            all_texts.extend(snippet.get('tags', []))
        
        channel_summary = analyze_channel_texts("\n".join(all_texts))
        if not channel_summary:
            continue

        rating = rate_channel_relevance(user_query, channel_summary)
        if not rating or 'score' not in rating:
            continue

        rated_channels.append({
            'title': channel_title,
            'thumbnail': channel['snippet']['thumbnails']['medium']['url'],
            'summary': channel_summary,
            'score': rating['score'],
            'reason': rating.get('reason', 'N/A')
        })

    sorted_channels = sorted(rated_channels, key=lambda x: x['score'], reverse=True)

    result_data = {
        'user_query': user_query,
        'keywords': structured_keywords, # 구조화된 키워드 전체를 전달
        'recommendations': sorted_channels
    }

    context = {'result_data': result_data}
    return render(request, 'frontend/partials/_search_results.html', context)

def load_chat_view(request, chat_id):
    """과거 채팅 기록 렌더링 (더미 데이터)"""
    # ... (이 부분은 현재 로직과 무관하므로 그대로 둡니다)

