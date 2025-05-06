import os
import json
import random
import requests
import time
from datetime import datetime, timedelta
from collections import Counter

class LottoAnalyzer:
    def __init__(self):
        self.lotto_data = []
        self.numbers_frequency = {}
        self.recent_numbers = []
        self.hot_numbers = []
        self.cold_numbers = []
        self.due_numbers = []
        self.data_path = 'data/lotto_data.json'
        self.recommendations_path = 'data/recommendations.json'
        self.results_path = 'data/results.json'
        
        # 데이터 디렉토리 확인
        os.makedirs('data', exist_ok=True)
        
        # 저장된 데이터가 있으면 로드
        self.load_data()
        
        # 저장된 추천 번호가 있으면 로드
        self.weekly_recommendations = self.load_recommendations()
    
    def load_data(self):
        """저장된 로또 데이터 불러오기"""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, 'r', encoding='utf-8') as file:
                    self.lotto_data = json.load(file)
                print(f"저장된 {len(self.lotto_data)}개의 로또 데이터를 불러왔습니다.")
                return True
            except Exception as e:
                print(f"데이터 불러오기 실패: {e}")
        return False
        
    def save_data(self):
        """로또 데이터 저장하기"""
        try:
            with open(self.data_path, 'w', encoding='utf-8') as file:
                json.dump(self.lotto_data, file, ensure_ascii=False, indent=2)
            print(f"{len(self.lotto_data)}개의 로또 데이터를 저장했습니다.")
            return True
        except Exception as e:
            print(f"데이터 저장 실패: {e}")
        return False
    
    def load_recommendations(self):
        """저장된 추천 번호 불러오기"""
        if os.path.exists(self.recommendations_path):
            try:
                with open(self.recommendations_path, 'r', encoding='utf-8') as file:
                    recommendations = json.load(file)
                print(f"저장된 추천 번호를 불러왔습니다.")
                return recommendations
            except Exception as e:
                print(f"추천 번호 불러오기 실패: {e}")
        return {}
    
    def save_recommendations(self, recommendations, week_key):
        """추천 번호 저장하기"""
        # 기존 추천 번호 불러오기
        all_recommendations = self.load_recommendations()
        
        # 새 추천 번호 추가
        all_recommendations[week_key] = recommendations
        
        try:
            with open(self.recommendations_path, 'w', encoding='utf-8') as file:
                json.dump(all_recommendations, file, ensure_ascii=False, indent=2)
            print(f"{week_key} 주간 추천 번호 {len(recommendations['combinations'])}개를 저장했습니다.")
            
            # 클래스 변수 업데이트
            self.weekly_recommendations = all_recommendations
            
            return True
        except Exception as e:
            print(f"추천 번호 저장 실패: {e}")
        return False
    
    def load_results(self):
        """저장된 결과 불러오기"""
        if os.path.exists(self.results_path):
            try:
                with open(self.results_path, 'r', encoding='utf-8') as file:
                    results = json.load(file)
                print(f"저장된 결과를 불러왔습니다.")
                return results
            except Exception as e:
                print(f"결과 불러오기 실패: {e}")
        return {}
    
    def save_results(self, results):
        """결과 저장하기"""
        try:
            with open(self.results_path, 'w', encoding='utf-8') as file:
                json.dump(results, file, ensure_ascii=False, indent=2)
            print(f"결과를 저장했습니다.")
            return True
        except Exception as e:
            print(f"결과 저장 실패: {e}")
        return False
        
    def get_latest_round(self):
        """최신 로또 회차 번호 가져오기"""
        try:
            # 회차를 1000으로 설정하고 API 호출 시도
            response = requests.get("https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo=1000")
            data = response.json()
            
            # 로또 번호가 없는 경우 (아직 해당 회차가 진행되지 않은 경우)
            if data.get('returnValue') == 'fail':
                # 최대 회차를 찾기 위해 이분 탐색
                min_round = 1
                max_round = 1000
                
                while min_round <= max_round:
                    mid_round = (min_round + max_round) // 2
                    
                    response = requests.get(f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={mid_round}")
                    data = response.json()
                    
                    if data.get('returnValue') == 'success':
                        min_round = mid_round + 1
                    else:
                        max_round = mid_round - 1
                
                return max_round
            else:
                # 임의로 큰 회차에서도 성공하면 회차별로 하나씩 확인
                current_round = 1000
                while True:
                    current_round += 1
                    response = requests.get(f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={current_round}")
                    data = response.json()
                    
                    if data.get('returnValue') == 'fail':
                        return current_round - 1
        except Exception as e:
            print(f"최신 회차 확인 실패: {e}")
            
            # 실패 시 저장된 데이터에서 최신 회차 가져오기
            if self.lotto_data:
                return self.lotto_data[0]['round']
            else:
                # 기본값 설정
                return 1170  # 임의의 기본값
    
    def fetch_lotto_data(self, start_round=1, end_round=None):
        """동행복권 API에서 로또 데이터 가져오기"""
        print("최근 로또 데이터를 가져오는 중입니다...")
        
        # 현재 회차 확인
        if end_round is None:
            end_round = self.get_latest_round()
            print(f"현재 최신 회차: {end_round}")
        
        # 이미 저장된 데이터가 있으면, 마지막 회차 다음부터 가져오기
        if self.lotto_data:
            start_round = max([data['round'] for data in self.lotto_data]) + 1
        
        # 가져올 회차 범위 설정
        if end_round - start_round > 50:
            print(f"데이터 부하를 줄이기 위해 최근 50회차만 분석합니다.")
            start_round = end_round - 49
            
        # 최신 데이터인 경우 가져오지 않음
        if start_round > end_round:
            print("이미 최신 데이터를 보유하고 있습니다.")
            return self.lotto_data
        
        print(f"{start_round}회차부터 {end_round}회차까지의 데이터를 가져옵니다.")
        
        new_data = []
        for round_num in range(start_round, end_round + 1):
            try:
                # 요청 간 간격을 두어 서버 부하 감소
                time.sleep(0.2)
                
                # API 호출
                url = f"https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={round_num}"
                response = requests.get(url)
                data = response.json()
                
                # API 응답 검증
                if data.get('returnValue') != 'success':
                    print(f"{round_num}회차 데이터가 없습니다.")
                    continue
                
                # 당첨번호 추출
                win_numbers = [
                    data.get('drwtNo1'),
                    data.get('drwtNo2'),
                    data.get('drwtNo3'),
                    data.get('drwtNo4'),
                    data.get('drwtNo5'),
                    data.get('drwtNo6')
                ]
                
                # 보너스 번호 추출
                bonus_number = data.get('bnusNo')
                
                # 추첨일자 추출 (API에서 밀리초 형식으로 제공)
                draw_date = data.get('drwNoDate')
                
                # 데이터 검증
                if None in win_numbers or bonus_number is None or draw_date is None:
                    print(f"{round_num}회차 데이터 불완전: {data}")
                    continue
                
                # 데이터 저장
                new_data.append({
                    'round': round_num,
                    'date': draw_date,
                    'numbers': win_numbers,
                    'bonus': bonus_number
                })
                
                print(f"{round_num}회차 데이터 로드 완료...")
            except Exception as e:
                print(f"{round_num}회차 데이터 가져오기 실패: {e}")
        
        # 새 데이터를 기존 데이터와 병합
        if new_data:
            # 회차 기준으로 정렬 (내림차순)
            self.lotto_data = sorted(
                self.lotto_data + new_data,
                key=lambda x: x['round'],
                reverse=True
            )
            # 데이터 저장
            self.save_data()
            
            # 최근 당첨번호 저장
            if self.lotto_data:
                self.recent_numbers = self.lotto_data[0]['numbers'] + [self.lotto_data[0]['bonus']]
        
        print(f"총 {len(self.lotto_data)}개의 회차 데이터를 보유하고 있습니다.")
        return self.lotto_data
    
    def analyze_frequency(self, periods=None):
        """번호별 출현 빈도 분석"""
        if not self.lotto_data:
            print("분석할 데이터가 없습니다. fetch_lotto_data()를 먼저 실행하세요.")
            return {}
        
        # 분석 기간 설정
        data_to_analyze = self.lotto_data
        if periods and periods < len(self.lotto_data):
            data_to_analyze = self.lotto_data[:periods]
        
        # 번호 빈도 계산
        all_numbers = []
        for data in data_to_analyze:
            all_numbers.extend(data['numbers'])
            all_numbers.append(data['bonus'])
        
        # 번호별 빈도 저장
        self.numbers_frequency = {num: all_numbers.count(num) for num in range(1, 46)}
        
        # Hot, Cold, Due 번호 분석
        sorted_freq = sorted(self.numbers_frequency.items(), key=lambda x: x[1], reverse=True)
        self.hot_numbers = [num for num, _ in sorted_freq[:10]]  # 가장 많이 나온 10개
        self.cold_numbers = [num for num, _ in sorted_freq[-10:]]  # 가장 적게 나온 10개
        
        # 최근 10회차 내에 나오지 않은 번호 추출
        recent_draws = []
        for i in range(min(10, len(data_to_analyze))):
            recent_draws.extend(data_to_analyze[i]['numbers'])
            recent_draws.append(data_to_analyze[i]['bonus'])
        
        self.due_numbers = [num for num in range(1, 46) if num not in recent_draws]
        
        return self.numbers_frequency
    
    def analyze_patterns(self):
        """당첨번호 패턴 분석"""
        if not self.lotto_data:
            print("분석할 데이터가 없습니다. fetch_lotto_data()를 먼저 실행하세요.")
            return {}
        
        patterns = {
            'odd_even_ratio': [],  # 홀짝 비율
            'high_low_ratio': [],  # 고저 비율 (1-22: 낮음, 23-45: 높음)
            'sum_numbers': [],     # 번호 합계
            'range_numbers': []    # 최대-최소 범위
        }
        
        for data in self.lotto_data:
            numbers = data['numbers']
            
            # 홀짝 비율
            odd_count = sum(1 for num in numbers if num % 2 == 1)
            patterns['odd_even_ratio'].append((odd_count, 6-odd_count))
            
            # 고저 비율
            low_count = sum(1 for num in numbers if num <= 22)
            patterns['high_low_ratio'].append((low_count, 6-low_count))
            
            # 번호 합계
            patterns['sum_numbers'].append(sum(numbers))
            
            # 최대-최소 범위
            patterns['range_numbers'].append(max(numbers) - min(numbers))
        
        # 패턴 요약
        pattern_summary = {}
        
        odd_even_common = Counter(patterns['odd_even_ratio']).most_common(3)
        pattern_summary['odd_even_common'] = odd_even_common
        
        high_low_common = Counter(patterns['high_low_ratio']).most_common(3)
        pattern_summary['high_low_common'] = high_low_common
        
        sum_avg = sum(patterns['sum_numbers']) / len(patterns['sum_numbers'])
        sum_min = min(patterns['sum_numbers'])
        sum_max = max(patterns['sum_numbers'])
        pattern_summary['sum_stats'] = {
            'avg': sum_avg,
            'min': sum_min,
            'max': sum_max
        }
        
        range_avg = sum(patterns['range_numbers']) / len(patterns['range_numbers'])
        pattern_summary['range_avg'] = range_avg
        
        return pattern_summary
    
    def recommend_numbers(self, num_combinations=30):
        """분석 결과를 바탕으로 로또 번호 추천"""
        if not self.numbers_frequency:
            self.analyze_frequency()
        
        pattern_summary = self.analyze_patterns()
        
        combinations = []
        for _ in range(num_combinations):
            # 번호 선택 전략 (여러 전략을 혼합하여 사용)
            # 1. 가중치 기반 선택 (출현 빈도에 비례)
            weights = [self.numbers_frequency[num] for num in range(1, 46)]
            pool = list(range(1, 46))
            
            # 2. 일부는 핫번호에서, 일부는 듀번호에서 선택
            hot_prob = random.random()  # 핫번호 선택 확률
            due_prob = random.random()  # 듀번호 선택 확률
            
            selected = []
            
            # 핫번호 1-2개 선택
            if hot_prob > 0.3 and self.hot_numbers:
                hot_count = random.randint(1, 2)
                selected.extend(random.sample(self.hot_numbers, min(hot_count, len(self.hot_numbers))))
            
            # 듀번호 1-2개 선택
            if due_prob > 0.4 and self.due_numbers:
                due_count = random.randint(1, 2)
                selected.extend(random.sample(self.due_numbers, min(due_count, len(self.due_numbers))))
            
            # 나머지 번호 가중치 기반으로 선택
            remaining = 6 - len(selected)
            if remaining > 0:
                # 이미 선택된 번호 제외
                remaining_pool = [num for num in pool if num not in selected]
                remaining_weights = [weights[num-1] for num in remaining_pool]
                
                # 가중치 기반 랜덤 선택
                additional = random.choices(
                    remaining_pool, 
                    weights=remaining_weights, 
                    k=remaining
                )
                selected.extend(additional)
            
            # 번호 정렬 후 저장
            selected.sort()
            combinations.append(selected)
        
        return combinations
        
    def generate_weekly_recommendations(self):
        """매주 일요일 오전 5시에 실행될 주간 번호 추천 생성 함수"""
        print(f"주간 로또 번호 추천 생성 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 데이터 업데이트
        self.fetch_lotto_data()
        
        # 빈도 분석
        self.analyze_frequency()
        
        # 30개 조합 생성
        combinations = self.recommend_numbers(30)
        
        # 이번 주 키 생성 (다음 추첨일 기준)
        now = datetime.now()
        days_until_saturday = (5 - now.weekday()) % 7  # 0=월요일, 6=일요일, 5=토요일까지 남은 일수
        if days_until_saturday == 0 and now.hour >= 20:  # 토요일 20시 이후면 다음 주 토요일
            days_until_saturday = 7
        
        next_saturday = now + timedelta(days=days_until_saturday)
        week_key = next_saturday.strftime('%Y-%m-%d')
        
        # 추천 번호 저장
        self.save_recommendations({
            'generated_at': now.strftime('%Y-%m-%d %H:%M:%S'),
            'target_date': week_key,
            'combinations': combinations
        }, week_key)
        
        print(f"주간 로또 번호 추천 생성 완료 - {week_key} 회차용 {len(combinations)}개 조합")
        
        return combinations
    
    def check_lottery_results(self):
        """매주 토요일 오후 10시에 실행될 로또 당첨 결과 확인 함수"""
        print(f"로또 당첨 결과 확인 시작 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 최신 당첨 정보 가져오기
        self.fetch_lotto_data()
        
        if not self.lotto_data:
            print("당첨 데이터가 없습니다.")
            return None
        
        # 가장 최근 당첨 번호
        latest_result = self.lotto_data[0]
        result_date = latest_result['date']
        result_numbers = latest_result['numbers']
        result_bonus = latest_result['bonus']
        
        print(f"최근 당첨 결과: {result_date}, 번호: {result_numbers}, 보너스: {result_bonus}")
        
        # 해당 날짜의 추천 번호가 있는지 확인
        recommendations = self.load_recommendations()
        
        # API에서 받은 날짜 형식 처리 (YYYY-MM-DD 형식으로 변환)
        try:
            date_obj = datetime.strptime(result_date, '%Y-%m-%d')
            result_key = date_obj.strftime('%Y-%m-%d')
        except ValueError:
            try:
                # 다른 날짜 형식 시도
                date_obj = datetime.strptime(result_date, '%Y/%m/%d')
                result_key = date_obj.strftime('%Y-%m-%d')
            except ValueError:
                print(f"날짜 형식 변환 실패: {result_date}")
                # 가장 가까운 토요일로 설정
                now = datetime.now()
                days_until_saturday = (5 - now.weekday()) % 7
                if days_until_saturday == 0 and now.hour >= 20:
                    days_until_saturday = 7
                closest_saturday = now - timedelta(days=7-days_until_saturday)
                result_key = closest_saturday.strftime('%Y-%m-%d')
        
        if result_key not in recommendations:
            # 가장 가까운 추천 찾기
            closest_key = None
            min_diff = float('inf')
            
            try:
                result_date_obj = datetime.strptime(result_key, '%Y-%m-%d')
                
                for key in recommendations:
                    try:
                        key_date_obj = datetime.strptime(key, '%Y-%m-%d')
                        diff = abs((result_date_obj - key_date_obj).days)
                        if diff < min_diff:
                            min_diff = diff
                            closest_key = key
                    except:
                        continue
                
                if closest_key and min_diff <= 7:  # 7일 이내에 가장 가까운 추천 사용
                    result_key = closest_key
                else:
                    print(f"{result_date} 해당 날짜의 추천 번호가 없습니다.")
                    return None
            except:
                print(f"날짜 비교 실패: {result_key}")
                if recommendations:
                    # 가장 최근 추천 사용
                    result_key = list(recommendations.keys())[-1]
                else:
                    print("추천 번호가 없습니다.")
                    return None
        
        # 추천 번호와 당첨 번호 비교
        weekly_recommendations = recommendations[result_key]['combinations']
        
        analysis_results = {
            'date': result_date,
            'round': latest_result['round'],
            'winning_numbers': result_numbers,
            'bonus_number': result_bonus,
            'match_counts': {
                '6': 0,  # 1등 (6개 일치)
                '5+bonus': 0,  # 2등 (5개 + 보너스)
                '5': 0,  # 3등 (5개 일치)
                '4': 0,  # 4등 (4개 일치)
                '3': 0,  # 5등 (3개 일치)
                '2': 0,  # 2개 일치 (당첨 아님)
                '1': 0,  # 1개 일치 (당첨 아님)
                '0': 0,  # 일치 없음 (당첨 아님)
            },
            'matched_combinations': {},
            'total_combinations': len(weekly_recommendations),
        }
        
        for i, combination in enumerate(weekly_recommendations):
            # 일치하는 번호 수 계산
            match_count = len(set(combination) & set(result_numbers))
            bonus_match = result_bonus in combination
            
            # 결과 카테고리 결정
            if match_count == 6:
                category = '6'  # 1등
            elif match_count == 5 and bonus_match:
                category = '5+bonus'  # 2등
            else:
                category = str(match_count)  # 3등~일치없음
            
            # 카운트 증가
            analysis_results['match_counts'][category] += 1
            
            # 매치된 조합 저장 (3개 이상 일치)
            if match_count >= 3 or (match_count == 5 and bonus_match):
                analysis_results['matched_combinations'][i] = {
                    'combination': combination,
                    'matched': list(set(combination) & set(result_numbers)),
                    'bonus_matched': bonus_match,
                    'category': category
                }
        
        # 결과 저장
        all_results = self.load_results()
        result_id = f"{latest_result['round']}_{result_key}"
        all_results[result_id] = analysis_results
        self.save_results(all_results)
        
        print(f"로또 당첨 결과 분석 완료: {result_key} - 1등: {analysis_results['match_counts']['6']}, 2등: {analysis_results['match_counts']['5+bonus']}, 3등: {analysis_results['match_counts']['5']}, 4등: {analysis_results['match_counts']['4']}, 5등: {analysis_results['match_counts']['3']}")
        
        return analysis_results