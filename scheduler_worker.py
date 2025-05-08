import os
import time
import schedule
from datetime import datetime

def run_scheduler():
    """스케줄러 실행 함수"""
    from analyzer import LottoAnalyzer
    analyzer = LottoAnalyzer()
    
    # 초기 추천 번호 생성
    if not os.path.exists('data/recommendations.json'):
        print(f"초기 추천 번호 생성 시작: {datetime.now()}")
        analyzer.generate_weekly_recommendations()
    
    # 스케줄 설정
    # 일요일 새벽 5시
    schedule.every().sunday.at("05:00").do(analyzer.generate_weekly_recommendations)
    # 토요일 밤 10시
    schedule.every().saturday.at("22:00").do(analyzer.check_lottery_results)
    
    print(f"스케줄러 시작 시간: {datetime.now()}")
    print("- 주간 번호 추천: 매주 일요일 오전 5시")
    print("- 당첨 결과 확인: 매주 토요일 오후 10시")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_scheduler()