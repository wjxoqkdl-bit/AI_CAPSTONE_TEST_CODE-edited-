from django.shortcuts import render
from django.conf import settings
import math
from datetime import datetime, timedelta

from gptAPI.services import extract_keywords, summarize_comments, analyze_channel_texts, rate_channel_relevance
from youtube_api.api_client import YouTubeDataCollector

def calculate_activity_score(video_count: int, last_upload_date: str) -> float:
    """채널의 활동성 점수를 계산 (0-100점 스케일)"""
    score = 0

    # 1. 영상 수 기반 점수 (로그 스케일)
    if video_count > 0:
        score += min(50, math.log(video_count + 1) * 10) # 최대 50점, 영상이 많을수록 점수 증가

    # 2. 최신성 기반 점수 (최대 50점)
    try:
        upload_dt = datetime.fromisoformat(last_upload_date.replace('Z', '+00:00'))
        now = datetime.now(upload_dt.tzinfo) # 현재 시간을 업로드 시간과 동일한 타임존으로
        days_since_upload = (now - upload_dt).days

        if days_since_upload <= 7: # 1주일 이내
            score += 50
        elif days_since_upload <= 30: # 1개월 이내
            score += 40
        elif days_since_upload <= 90: # 3개월 이내
            score += 20
        elif days_since_upload <= 180: # 6개월 이내
            score += 10
        # 6개월 이상은 추가 점수 없음

    except ValueError:
        pass # 날짜 파싱 오류 시 점수 추가 없음

    return min(100, max(0, score)) # 0-100점 범위 유지

def calculate_reliability_score(subscriber_count: int, view_count: int, like_count: int, dislike_count: int, video_duration_avg_seconds: int) -> float:
    """채널의 신뢰도 점수 계산 (0-100점 스케일)"""
    score = 0

    # 1. 구독자 수 기반 점수 (로그 스케일)
    if subscriber_count > 0:
        score += min(30, math.log(subscriber_count + 1) * 3) # 최대 30점

    # 2. 좋아요/싫어요 비율 기반 점수 (최대 30점)
    total_reactions = like_count + dislike_count
    if total_reactions > 0:
        like_ratio = like_count / total_reactions
        score += like_ratio * 30 # 좋아요 비율이 높을수록 점수 증가

    # 3. 평균 비디오 길이 기반 점수 (최대 20점)
    # 너무 짧은 영상만 있는 채널은 감점
    if video_duration_avg_seconds > 0:
        if video_duration_avg_seconds >= 600: # 10분 이상
            score += 20
        elif video_duration_avg_seconds >= 300: # 5분 이상
            score += 15
        elif video_duration_avg_seconds >= 180: # 3분 이상
            score += 10
        else: # 3분 미만은 감점
            score += 5

    # 4. 조회수 대비 구독자 수 비율 (최대 20점)
    # 비정상적으로 조회수만 높은 채널 (봇 의심) 감점
    if subscriber_count > 0 and view_count > 0:
        views_per_sub = view_count / subscriber_count
        if views_per_sub < 10: # 구독자 대비 조회수가 너무 낮으면 감점
            score += 10
        elif views_per_sub < 100: # 적정 범위
            score += 20
        elif views_per_sub > 1000: # 구독자 대비 조회수가 너무 높으면 감점
            score += 5

    return min(100, max(0, score)) # 0-100점 범위 유지

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

    search_queries = extract_keywords(user_query)
    if not search_queries:
        return render(request, 'frontend/partials/_error.html', {'message': '키워드를 추출하지 못했습니다.'})

    youtube_api_key = getattr(settings, 'YOUTUBE_API_KEY', None)
    if not youtube_api_key:
        return render(request, 'frontend/partials/_error.html', {'message': 'YOUTUBE_API_KEY가 설정되지 않았습니다.'})

    collector = YouTubeDataCollector(youtube_api_key)
    
    try:
        # 다중 키워드로 교차 검색 및 후보군 통합
        candidate_channels = {}
        for query in search_queries:
            found_channels = collector.search_channels(keyword=query, max_results=5) # 검색어당 5개씩
            for channel in found_channels:
                channel_id = channel['id']['channelId']
                if channel_id not in candidate_channels:
                    candidate_channels[channel_id] = channel # 중복 제거하며 추가
    except Exception as e:
        # HttpError를 포함한 모든 API 관련 예외 처리
        return render(request, 'frontend/partials/_error.html', {'message': f'YouTube API 호출 중 오류가 발생했습니다: {e}'})

    rated_channels = []
    for channel_id, channel in candidate_channels.items():
        channel_title = channel['snippet']['title']
        channel_description = channel['snippet']['description']

        # 채널 상세 정보 가져오기 (영상 수, 구독자 수 포함)
        channel_details = collector.get_channel_details(channel_id)
        subscriber_count = int(channel_details.get('statistics', {}).get('subscriberCount', 0)) if channel_details else 0
        video_count = int(channel_details.get('statistics', {}).get('videoCount', 0)) if channel_details else 0
        view_count = int(channel_details.get('statistics', {}).get('viewCount', 0)) if channel_details else 0

        # 최신 영상 업로드 날짜 가져오기
        latest_videos_snippet = collector.get_latest_videos(channel_id, max_results=1)
        last_upload_date = latest_videos_snippet[0]['snippet']['publishedAt'] if latest_videos_snippet else None

        # 활동성 점수 계산
        activity_score = 0
        if last_upload_date:
            activity_score = calculate_activity_score(video_count, last_upload_date)

        # 비디오 텍스트 데이터 수집 (기존 로직)
        latest_videos = collector.get_latest_videos(channel_id, max_results=3)
        video_ids = [video['id']['videoId'] for video in latest_videos]
        video_details = collector.get_video_details(video_ids)

        # 비디오 통계 (좋아요/싫어요, 길이) 수집
        total_likes = 0
        total_dislikes = 0
        total_duration_seconds = 0
        video_count_for_avg = 0

        for detail in video_details:
            stats = detail.get('statistics', {})
            content_details = detail.get('contentDetails', {})
            
            total_likes += int(stats.get('likeCount', 0))
            # YouTube API v3에서는 dislikeCount가 더 이상 직접 제공되지 않으므로, 0으로 가정하거나 다른 방식으로 추정해야 합니다.
            # 여기서는 단순화를 위해 0으로 처리합니다.
            total_dislikes += int(stats.get('dislikeCount', 0)) # v3에서는 항상 0일 수 있음

            # 비디오 길이 파싱 (ISO 8601 duration format)
            duration_str = content_details.get('duration', 'PT0S')
            duration_seconds = parse_duration_to_seconds(duration_str)
            total_duration_seconds += duration_seconds
            video_count_for_avg += 1

        video_duration_avg_seconds = total_duration_seconds / video_count_for_avg if video_count_for_avg > 0 else 0

        # 신뢰도 점수 계산
        reliability_score = calculate_reliability_score(subscriber_count, view_count, total_likes, total_dislikes, video_duration_avg_seconds)

        all_texts = [channel_title, channel_description]
        for detail in video_details:
            snippet = detail.get('snippet', {})
            all_texts.append(snippet.get('title', ''))
            all_texts.append(snippet.get('description', ''))
            all_texts.extend(snippet.get('tags', []))
        
        channel_summary = analyze_channel_texts("\n".join(all_texts))
        if not channel_summary:
            continue

        # AI 관련성 점수
        ai_relevance_rating = rate_channel_relevance(user_query, channel_summary)
        ai_score = ai_relevance_rating.get('score', 0) if ai_relevance_rating else 0

        # 최종 점수 계산 (AI 관련성 60%, 활동성 20%, 신뢰도 20% 가중치)
        final_score = (ai_score * 0.6) + (activity_score * 0.2) + (reliability_score * 0.2)

        rated_channels.append({
            'title': channel_title,
            'thumbnail': channel['snippet']['thumbnails']['medium']['url'],
            'summary': channel_summary,
            'ai_score': ai_score,
            'activity_score': activity_score,
            'reliability_score': reliability_score, # 신뢰도 점수 추가
            'final_score': round(final_score, 2),
            'reason': ai_relevance_rating.get('reason', 'N/A')
        })

    sorted_channels = sorted(rated_channels, key=lambda x: x['final_score'], reverse=True)

    result_data = {
        'user_query': user_query,
        'keywords': search_queries,
        'recommendations': sorted_channels
    }

    context = {'result_data': result_data}
    return render(request, 'frontend/partials/_search_results.html', context)

def parse_duration_to_seconds(duration_str: str) -> int:
    """ISO 8601 형식의 비디오 길이를 초 단위로 파싱"""
    # 예: PT1H30M5S -> 1시간 30분 5초
    total_seconds = 0
    if 'H' in duration_str:
        hours = int(duration_str.split('H')[0].replace('PT', ''))
        total_seconds += hours * 3600
        duration_str = duration_str.split('H')[1]
    if 'M' in duration_str:
        minutes = int(duration_str.split('M')[0].replace('PT', ''))
        total_seconds += minutes * 60
        duration_str = duration_str.split('M')[1]
    if 'S' in duration_str:
        seconds = int(duration_str.split('S')[0].replace('PT', ''))
        total_seconds += seconds
    return total_seconds

def load_chat_view(request, chat_id):
    """과거 채팅 기록 렌더링 (더미 데이터)"""
    # 임시 응답 추가
    return render(request, 'frontend/search.html', {'chat_id': chat_id, 'message': '과거 채팅 기록 로드 예정'})
