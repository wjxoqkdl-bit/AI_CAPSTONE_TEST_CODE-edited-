# wjxoqkdl-bit/ai_capstone_test_code-edited-/.../frontend/views.py

from django.shortcuts import render
from django.conf import settings
import math
from datetime import datetime, timedelta

from gptAPI.services import extract_keywords, summarize_comments, analyze_channel_texts, rate_channel_relevance
from youtube_api.api_client import YouTubeDataCollector


# [유지] parse_duration_to_seconds 함수 (상단 위치)
def parse_duration_to_seconds(duration_str: str) -> int:
    """ISO 8601 형식의 비디오 길이를 초 단위로 파싱"""
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


def calculate_activity_score(video_count: int, last_upload_date: str) -> float:
    # ... (기존과 동일) ...
    score = 0
    if video_count > 0:
        score += min(50, math.log(video_count + 1) * 10)
    try:
        upload_dt = datetime.fromisoformat(last_upload_date.replace('Z', '+00:00'))
        now = datetime.now(upload_dt.tzinfo)
        days_since_upload = (now - upload_dt).days
        if days_since_upload <= 7:
            score += 50
        elif days_since_upload <= 30:
            score += 40
        elif days_since_upload <= 90:
            score += 20
        elif days_since_upload <= 180:
            score += 10
    except ValueError:
        pass
    return min(100, max(0, score))


def calculate_reliability_score(subscriber_count: int, view_count: int, like_count: int, dislike_count: int,
                                video_duration_avg_seconds: int) -> float:
    # ... (기존과 동일) ...
    score = 0
    if subscriber_count > 0:
        score += min(30, math.log(subscriber_count + 1) * 3)
    total_reactions = like_count + dislike_count
    if total_reactions > 0:
        like_ratio = like_count / total_reactions
        score += like_ratio * 30
    if video_duration_avg_seconds > 0:
        if video_duration_avg_seconds >= 600:
            score += 20
        elif video_duration_avg_seconds >= 300:
            score += 15
        elif video_duration_avg_seconds >= 180:
            score += 10
        else:
            score += 5
    if subscriber_count > 0 and view_count > 0:
        views_per_sub = view_count / subscriber_count
        if views_per_sub < 10:
            score += 10
        elif views_per_sub < 100:
            score += 20
        elif views_per_sub > 1000:
            score += 5
    return min(100, max(0, score))


def login_view(request):
    """로그인 페이지 렌더링"""
    return render(request, 'frontend/login.html')


def search_page_view(request):
    """메인 검색 페이지 렌더링 (더미 데이터 포함)"""
    # [유지] 사이드바는 (DB 연동 전까지) 더미 데이터로 유지
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

    if not settings.YOUTUBE_API_KEYS:
        return render(request, 'frontend/partials/_error.html', {'message': 'YOUTUBE_API_KEY가 설정되지 않았습니다.'})

    collector = YouTubeDataCollector()

    try:
        candidate_channels = {}
        for query in search_queries:
            found_channels = collector.search_channels(keyword=query, max_results=5)
            for channel in found_channels:
                channel_id = channel['id']['channelId']
                if channel_id not in candidate_channels:
                    candidate_channels[channel_id] = channel
    except Exception as e:
        return render(request, 'frontend/partials/_error.html', {'message': f'YouTube API 호출 중 오류가 발생했습니다: {e}'})

    rated_channels = []
    for channel_id, channel in candidate_channels.items():
        channel_title = channel['snippet']['title']
        channel_description = channel['snippet']['description']
        channel_details = collector.get_channel_details(channel_id)
        subscriber_count = int(
            channel_details.get('statistics', {}).get('subscriberCount', 0)) if channel_details else 0
        video_count = int(channel_details.get('statistics', {}).get('videoCount', 0)) if channel_details else 0
        view_count = int(channel_details.get('statistics', {}).get('viewCount', 0)) if channel_details else 0
        latest_videos = collector.get_latest_videos(channel_id, max_results=3)
        latest_videos_snippet = collector.get_latest_videos(channel_id, max_results=1)
        last_upload_date = latest_videos_snippet[0]['snippet']['publishedAt'] if latest_videos_snippet else None
        activity_score = 0
        if last_upload_date:
            activity_score = calculate_activity_score(video_count, last_upload_date)
        video_ids = [video['snippet']['resourceId']['videoId'] for video in latest_videos if
                     video.get('snippet', {}).get('resourceId', {}).get('videoId')]

        # [수정] 👈 1단계에서 ",status"를 추가했기 때문에 video_details가 'status' 정보를 포함하게 됩니다.
        video_details = collector.get_video_details(video_ids)

        # [수정] 👈 153 오류의 근본 원인 해결!
        # '90초(Shorts) 거르기' 로직 대신, '퍼가기 가능(embeddable)' 여부를 직접 확인합니다.
        latest_video_id = None  # 일단 None으로 초기화
        for detail in video_details:
            # [수정] 'status' 객체에서 'embeddable' 값이 True인지 직접 확인
            if detail.get('status', {}).get('embeddable') is True:
                latest_video_id = detail['id']
                break  # '퍼가기 가능한' 영상을 찾았으면 루프 종료

        # (예외처리 로직: 'embeddable'한 영상이 하나도 없으면 latest_video_id는 None으로 유지됨)

        total_likes = 0
        total_dislikes = 0
        total_duration_seconds = 0
        video_count_for_avg = 0
        for detail in video_details:
            stats = detail.get('statistics', {})
            content_details = detail.get('contentDetails', {})
            total_likes += int(stats.get('likeCount', 0))
            total_dislikes += int(stats.get('dislikeCount', 0))
            duration_str = content_details.get('duration', 'PT0S')
            duration_seconds = parse_duration_to_seconds(duration_str)
            total_duration_seconds += duration_seconds
            video_count_for_avg += 1
        video_duration_avg_seconds = total_duration_seconds / video_count_for_avg if video_count_for_avg > 0 else 0
        reliability_score = calculate_reliability_score(subscriber_count, view_count, total_likes, total_dislikes,
                                                        video_duration_avg_seconds)
        all_texts = [channel_title, channel_description]
        for detail in video_details:
            snippet = detail.get('snippet', {})
            all_texts.append(snippet.get('title', ''))
            all_texts.append(snippet.get('description', ''))
            all_texts.extend(snippet.get('tags', []))
        channel_summary = analyze_channel_texts("\n".join(all_texts))
        if not channel_summary:
            continue
        ai_relevance_rating = rate_channel_relevance(user_query, channel_summary)
        ai_score = ai_relevance_rating.get('score', 0) if ai_relevance_rating else 0
        final_score = (ai_score * 0.6) + (activity_score * 0.2) + (reliability_score * 0.2)

        # [유지] 템플릿에 하이퍼링크(channel_id)와 iframe(latest_video_id) 데이터를 전달
        rated_channels.append({
            'channel_id': channel_id,
            'title': channel_title,
            'thumbnail': channel['snippet']['thumbnails']['medium']['url'],
            'summary': channel_summary,
            'ai_score': ai_score,
            'activity_score': activity_score,
            'reliability_score': reliability_score,
            'final_score': round(final_score, 2),
            'reason': ai_relevance_rating.get('reason', 'N/A'),
            'latest_video_id': latest_video_id  # [수정]에서 찾은 'embeddable'한 ID를 전달
        })

    sorted_channels = sorted(rated_channels, key=lambda x: x['final_score'], reverse=True)
    result_data = {
        'user_query': user_query,
        'keywords': search_queries,
        'recommendations': sorted_channels
    }
    context = {'result_data': result_data}
    return render(request, 'frontend/partials/_search_results.html', context)


def load_chat_view(request, chat_id):
    """과거 채팅 기록 렌더링 (더미 데이터)"""
    return render(request, 'frontend/search.html', {'chat_id': chat_id, 'message': '과거 채팅 기록 로드 예정'})