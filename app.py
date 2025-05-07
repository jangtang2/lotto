import threading
import time
import schedule
from datetime import datetime

def run_scheduler():
    from analyzer import LottoAnalyzer
    analyzer = LottoAnalyzer()
    
    # 초기 추천 번호 생성
    if not os.path.exists('data/recommendations.json'):
        analyzer.generate_weekly_recommendations()
    
    # 스케줄 설정
    # 일요일 새벽 5시
    schedule.every().sunday.at("05:00").do(analyzer.generate_weekly_recommendations)
    # 토요일 밤 10시
    schedule.every().saturday.at("22:00").do(analyzer.check_lottery_results)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# 백그라운드에서 스케줄러 실행
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()