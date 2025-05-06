from analyzer import LottoAnalyzer
from datetime import datetime, timedelta
import random

def create_test_result():
    """테스트용 당첨 결과 생성 함수"""
    analyzer = LottoAnalyzer()
    
    # 테스트 데이터 생성을 위해 추천 번호 생성
    if not analyzer.weekly_recommendations:
        print("추천 번호가 없습니다. 먼저 추천 번호를 생성합니다.")
        analyzer.generate_weekly_recommendations()
    
    # 저장된 추천 번호 확인
    now = datetime.now()
    days_until_saturday = (5 - now.weekday()) % 7
    if days_until_saturday == 0 and now.hour >= 20:  # 토요일 20시 이후면 다음 주 토요일
        days_until_saturday = 7
    
    next_saturday = now - timedelta(days=2)  # 지난 주 토요일로 설정
    week_key = next_saturday.strftime('%Y-%m-%d')
    
    # 저장된 추천 번호 확인
    all_recommendations = analyzer.load_recommendations()
    if week_key not in all_recommendations:
        print(f"{week_key} 날짜에 해당하는 추천 번호가 없습니다.")
        # 가장 최근 추천 사용
        if all_recommendations:
            keys = list(all_recommendations.keys())
            week_key = keys[-1]
            print(f"가장 최근 추천 ({week_key}) 사용")
        else:
            print("추천 번호가 없습니다. 종료합니다.")
            return
    
    weekly_recommendations = all_recommendations[week_key]['combinations']
    
    # 임의의 당첨 번호 생성 (추천 번호 중에서 일부가 당첨되도록)
    if len(weekly_recommendations) >= 3:
        winning_combination = weekly_recommendations[0][:4]  # 첫 번째 조합에서 4개 선택
        winning_combination.extend(random.sample([num for num in range(1, 46) if num not in winning_combination], 2))
        bonus_number = random.choice([num for num in range(1, 46) if num not in winning_combination])
    else:
        winning_combination = random.sample(range(1, 46), 6)
        bonus_number = random.choice([num for num in range(1, 46) if num not in winning_combination])
    
    winning_combination.sort()
    
    # 결과 객체 생성
    latest_result = {
        'round': 1170,  # 임의의 회차
        'date': week_key,
        'numbers': winning_combination,
        'bonus': bonus_number
    }
    
    # 저장된 데이터에 추가
    analyzer.lotto_data.insert(0, latest_result)
    analyzer.save_data()
    
    print(f"테스트 당첨 결과 생성 완료: {latest_result}")
    
    # 당첨 결과 확인 로직 실행
    result = analyzer.check_lottery_results()
    
    print("테스트 당첨 결과 저장 완료")
    return result

if __name__ == "__main__":
    result = create_test_result()
    if result:
        print("테스트 당첨 결과 요약:")
        print(f"1등 (6개 일치): {result['match_counts']['6']}개")
        print(f"2등 (5개+보너스): {result['match_counts']['5+bonus']}개")
        print(f"3등 (5개 일치): {result['match_counts']['5']}개")
        print(f"4등 (4개 일치): {result['match_counts']['4']}개")
        print(f"5등 (3개 일치): {result['match_counts']['3']}개")