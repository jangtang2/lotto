import os
import random
from datetime import datetime, timedelta
from flask import render_template, jsonify, request, redirect, url_for, session
from analyzer import LottoAnalyzer
from templates import create_templates

# 애플리케이션 초기화 시 실행할 함수
def setup_app():
    """애플리케이션 초기화 시 실행할 설정"""
    # 템플릿 디렉토리 확인 및 생성
    os.makedirs('templates', exist_ok=True)
    
    # 템플릿 파일 생성
    create_templates()

def register_routes(app):
    """Flask 애플리케이션에 라우트 등록"""
    
    # 애플리케이션 초기화 시 설정 실행
    setup_app()
    
    @app.route('/')
    def index():
        """통합 메인 페이지 - 번호 추천 및 당첨 결과 확인"""
        # 분석기 인스턴스 생성
        analyzer = LottoAnalyzer()
        
        # 데이터 로드
        analyzer.fetch_lotto_data()
        
        # 빈도 분석
        analyzer.analyze_frequency()
        
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
            # 30개 번호 조합 생성
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
        
        # 최근 당첨 번호
        recent_data = analyzer.lotto_data[:3] if analyzer.lotto_data else []
        
        # 핫, 콜드, 듀 번호
        number_stats = {
            'hot_numbers': analyzer.hot_numbers[:6],  # 상위 6개만
            'cold_numbers': analyzer.cold_numbers[:6],  # 상위 6개만
            'due_numbers': analyzer.due_numbers[:6] if len(analyzer.due_numbers) >= 6 else analyzer.due_numbers  # 최대 6개
        }
        
        return render_template(
            'index.html',
            combinations=selected_combinations,
            total_combinations=len(all_combinations),
            target_date=week_key,
            generated_at=generation_time,
            recent_data=recent_data,
            number_stats=number_stats,
            results=sorted_results[:1] if sorted_results else []  # 가장 최근 결과만
        )
    
    @app.route('/refresh-combinations')
    def refresh_combinations():
        """추천 번호 새로고침"""
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