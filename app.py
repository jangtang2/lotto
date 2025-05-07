import os
from flask import Flask
import threading
import time
import schedule
from datetime import datetime

# Flask 애플리케이션 생성
app = Flask(__name__)
app.secret_key = os.urandom(24)  # 세션 암호화를 위한 키

# Jinja2에 min 및 max 함수 추가
app.jinja_env.globals.update(min=min, max=max)

def run_scheduler():
    """내장 스케줄러 실행 함수"""
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
    
    print("스케줄러가 시작되었습니다.")
    print("- 주간 번호 추천: 매주 일요일 오전 5시")
    print("- 당첨 결과 확인: 매주 토요일 오후 10시")
    
    while True:
        schedule.run_pending()
        time.sleep(60)

# 스케줄러 시작
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

# 라우트 등록
from routes import register_routes
register_routes(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)