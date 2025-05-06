import threading
import schedule
import time
from datetime import datetime
from analyzer import LottoAnalyzer

def start_scheduler():
    """백그라운드에서 스케줄러 시작"""
    # 분석기 인스턴스 생성
    analyzer = LottoAnalyzer()
    
    # 일요일 오전 5시에 주간 번호 추천 생성
    schedule.every().sunday.at("05:00").do(analyzer.generate_weekly_recommendations)
    
    # 토요일 오후 10시에 당첨 결과 확인
    schedule.every().saturday.at("22:00").do(analyzer.check_lottery_results)
    
    # 초기 데이터 로드
    analyzer.fetch_lotto_data()
    
    print("스케줄러가 시작되었습니다.")
    print("- 주간 번호 추천: 매주 일요일 오전 5시")
    print("- 당첨 결과 확인: 매주 토요일 오후 10시")
    
    # 백그라운드 스레드에서 스케줄러 실행
    scheduler_thread = threading.Thread(target=_run_scheduler)
    scheduler_thread.daemon = True  # 메인 스레드 종료시 함께 종료
    scheduler_thread.start()

def _run_scheduler():
    """스케줄러 실행 루프"""
    while True:
        schedule.run_pending()
        time.sleep(60)  # 1분마다 스케줄 확인