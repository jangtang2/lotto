import os
import random
from datetime import datetime, timedelta
from flask import render_template, jsonify, request, redirect, url_for, session
from analyzer import LottoAnalyzer
from templates import create_templates

# 전역 분석기 인스턴스 생성
analyzer = LottoAnalyzer()

# 애플리케이션 초기화 시 실행할 함수
def setup_app():
    """애플리케이션 초기화 시 실행할 설정"""
    global analyzer
    
    # 템플릿 디렉토리 확인 및 생성
    os.makedirs('templates', exist_ok=True)
    
    # 템플릿 파일 생성
    create_templates()
    
    # 초기 데이터 로드
    analyzer.fetch_lotto_data()
    analyzer.analyze_frequency()

def register_routes(app):
    """Flask 애플리케이션에 라우트 등록"""
    
    # 애플리케이션 초기화 시 설정 실행
    setup_app()
    
    @app.route('/')
    def index():
        """통합 메인 페이지 - 번호 추천 및 당첨 결과 확인"""
        global analyzer
        
        # 저장된 추천 번호 확인
        now = datetime.now()
        days_until_saturday = (5 - now.weekday()) % 7
        if days_until_saturday == 0 and now.hour >= 20:  # 토요일 20시 이후면 다음 주 토요일
            days_until_saturday = 7
        
        next_saturday = now + timedelta(days=days_until_saturday)
        week_key = next_saturday.strftime('%Y-%m-%d')
        
        # 저장된 추천 번호 확인
        if week_key in analyzer.weekly_recommendations:
            all_combinations = analyzer.weekly_recommendations[week_key]['combinations']
            generation_time = analyzer.weekly_recommendations[week_key]['generated_at']
        else:
            # 이미 분석된 데이터가 있으므로 번호 생성만 수행
            all_combinations = analyzer.recommend_numbers(30)
            generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 세션에만 저장 (스케줄러가 일요일에 정식으로 생성)
            analyzer.save_recommendations({
                'generated_at': generation_time,
                'target_date': week_key,
                'combinations': all_combinations
            }, week_key)
        
        # 세션에 모든 조합 저장
        session['all_combinations'] = all_combinations
        session['week_key'] = week_key
        session['generation_time'] = generation_time
        
        # 5개 랜덤 선택
        if len(all_combinations) > 5:
            selected_combinations = random.sample(all_combinations, 5)
        else:
            selected_combinations = all_combinations
        
        # 최근 당첨 결과 가져오기
        all_results = analyzer.load_results()
        
        # 결과 정렬 (최신순)
        sorted_results = sorted(
            all_results.items(), 
            key=lambda x: x[1].get('round', 0), 
            reverse=True
        )
        
        return render_template(
            'index.html',
            combinations=selected_combinations,
            total_combinations=len(all_combinations),
            target_date=week_key,
            generated_at=generation_time,
            results=sorted_results[:1] if sorted_results else []  # 가장 최근 결과만
        )
    
    @app.route('/refresh-combinations')
    def refresh_combinations():
        """추천 번호 새로고침 (데이터 로드 없이 세션에서 가져옴)"""
        # 세션에서 모든 조합 가져오기
        all_combinations = session.get('all_combinations', [])
        
        # 5개 랜덤 선택
        if len(all_combinations) > 5:
            selected_combinations = random.sample(all_combinations, 5)
        else:
            selected_combinations = all_combinations
        
        return render_template(
            'combinations_partial.html',
            combinations=selected_combinations
        )
    
    @app.route('/analyze')
    def analyze():
        """로또 번호 분석 페이지 (백업용)"""
        return redirect(url_for('index'))
    
    @app.route('/recommend')
    def recommend():
        """로또 번호 추천 페이지 (백업용)"""
        return redirect(url_for('index'))
    
    @app.route('/results')
    def results():
        """로또 번호 당첨 결과 페이지 (백업용)"""
        return redirect(url_for('index'))
    
    @app.route('/nfc-setup')
    def nfc_setup():
        """NFC 태그 설정 페이지"""
        return render_template('nfc_setup.html')
    
    @app.route('/generate-nfc-data', methods=['POST'])
    def generate_nfc_data():
        """NFC 태그에 기록할 데이터 생성"""
        base_url = request.form.get('base_url', request.host_url)
        access_type = request.form.get('access_type', '')
        
        # NFC 태그에 기록할 URL
        nfc_url = f"{base_url}{access_type}"
        
        # NFC 태그를 위한 안드로이드 앱 인텐트 형식 (대부분의 NFC 태그 앱과 호환)
        android_nfc_intent = f"android-app://com.android.chrome/https/{nfc_url.replace('https://', '')}"
        
        return jsonify({
            'url': nfc_url,
            'android_intent': android_nfc_intent,
            'description': f"이 태그는 로또 번호 분석 및 추천 애플리케이션{'의 ' + access_type + ' 페이지' if access_type else ''}로 연결됩니다."
        })
    
    @app.route('/cron/generate-recommendations', methods=['POST'])
    def cron_generate_recommendations():
        """GitHub Actions에서 호출하는 추천 번호 생성"""
        # GitHub Actions의 IP를 확인하거나 간단한 인증 추가 가능
        user_agent = request.headers.get('User-Agent', '')
        if 'curl' not in user_agent:
            return "Unauthorized", 401
        
        try:
            from analyzer import LottoAnalyzer
            analyzer = LottoAnalyzer()
            analyzer.generate_weekly_recommendations()
            return {"status": "success", "message": "Recommendations generated"}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500
    
    @app.route('/cron/check-results', methods=['POST'])
    def cron_check_results():
        """GitHub Actions에서 호출하는 당첨 결과 확인"""
        user_agent = request.headers.get('User-Agent', '')
        if 'curl' not in user_agent:
            return "Unauthorized", 401
        
        try:
            from analyzer import LottoAnalyzer
            analyzer = LottoAnalyzer()
            analyzer.check_lottery_results()
            return {"status": "success", "message": "Results checked"}, 200
        except Exception as e:
            return {"status": "error", "message": str(e)}, 500