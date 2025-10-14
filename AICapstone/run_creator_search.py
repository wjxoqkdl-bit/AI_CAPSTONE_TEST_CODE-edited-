import os
import json
from dotenv import load_dotenv
from youtube_api.api_client import YouTubeDataCollector

def main():
    # 1. .env 파일에서 API 키 로드
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("오류: .env 파일에 YOUTUBE_API_KEY를 설정해주세요.")
        return

    # 2. (AI가 선별했다고 가정한) 크리에이터 ID 리스트
    # 실제로는 이 리스트를 AI Agent로부터 전달받게 됩니다.
    TARGET_CREATOR_IDS = [
        "UCSCJdSHX9hE4ylwTVMJXxLQ",  # 잇섭
        "UCULRVjf5z_WoR106msn8HoA",  # 슈카월드
        "UCIs6AoWiNrN3P7fQqsxNncA"   # 침착맨
    ]

    # 3. 데이터 수집기 생성 및 메인 함수 호출
    collector = YouTubeDataCollector(api_key)
    # ID 리스트를 직접 전달하여 데이터 수집 실행
    creator_data = collector.get_creator_data_by_ids(TARGET_CREATOR_IDS)

    # 4. 수집된 데이터 확인 및 파일 저장
    if creator_data:
        output_filename = "creator_data_by_ids.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(creator_data, f, indent=4, ensure_ascii=False)
        
        print(f"\n✅ 데이터 수집 완료! '{output_filename}' 파일로 저장되었습니다.")
    else:
        print("데이터를 수집하지 못했습니다.")

if __name__ == "__main__":
    main()