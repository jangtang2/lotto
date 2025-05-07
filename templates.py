import os

def create_templates():
    """기본 HTML 템플릿 파일 생성"""
    templates = {
        'index.html': '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>로또 번호 분석 및 추천</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
    <style>
        body {
            background-color: #9bd2b7;
            padding-bottom: 30px;
            font-size: 14px;
            max-width: 100%;
            overflow-x: hidden;
        }
        .container {
            width: 90%;
            max-width: 90%;
        }
        .card {
            margin-bottom: 15px;
            box-shadow: 0 3px 5px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            width: 100%;
        }
        .card:hover {
            transform: translateY(-3px);
        }
        .card-header {
            padding: 8px 12px;
        }
        .card-body {
            padding: 10px 12px;
        }
        .lotto-ball {
            display: inline-flex;
            width: 7vw;
            height: 7vw;
            border-radius: 50%;
            color: white;
            font-weight: bold;
            text-align: center;
            justify-content: center;
            align-items: center;
            margin: 0 2px;
            font-size: 11px;
        }
        /* 숫자별 색상 */
        .ball-1-10 { background-color: #ff6b6b; }
        .ball-11-20 { background-color: #ffa94d; }
        .ball-21-30 { background-color: #74c0fc; }
        .ball-31-40 { background-color: #69db7c; }
        .ball-41-45 { background-color: #9775fa; }
        /* 보너스 볼 */
        .bonus { background-color: #495057; }
        .footer {

            padding: 15px 0;
            
            text-align: center;
            font-size: 12px;
        }
        .match-count {
            font-size: 1.1rem;
            font-weight: bold;
        }
        .match-1, .match-2 { color: #6c757d; } /* 미당첨 */
        .match-3 { color: #28a745; } /* 5등 */
        .match-4 { color: #007bff; } /* 4등 */
        .match-5 { color: #fd7e14; } /* 3등 */
        .match-5bonus { color: #dc3545; } /* 2등 */
        .match-6 { color: #9c27b0; } /* 1등 */
        .section-title {
            border-left: 4px solid #007bff;
            padding-left: 8px;
            margin: 20px 0 15px;
            font-size: 18px;
        }
        .header-img {
            width: 100%;
            max-width: 450px;
            display: block;
        }
        .table {
            font-size: 13px;
        }
        .table th{
            padding: 8px 6px;
        }
        .table td {
            padding: 8px 4px;
            vertical-align: middle;
        }
        h4 {
            font-size: 16px;
            margin: 0;
        }
        h5 {
            font-size: 15px;
            margin-bottom: 8px;
        }
        p {
            margin-bottom: 8px;
        }
    </style>
</head>
<body>

        <img src="{{ url_for('static', filename='Jackpot.png') }}" alt="HEAD.PNG" class="header-img" >

    
    <div class="container">
        <!-- 추천 번호 -->
        <div class="row justify-content-center">
            <div class="col-12">
                <div class="card">
                    
                    <div class="card-body">
                        <div class="mb-2">
                            <p><strong>추첨일:</strong> {{ target_date }}</p>
                        </div>
                        
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th width="20%">번호</th>
                                        <th width="80%">추천 조합</th>
                                    </tr>
                                </thead>
                                <tbody id="combinations-container">
                                    {% for combination in combinations %}
                                    <tr>
                                        <td>행운 {{ loop.index }}</td>
                                        <td>
                                            {% for num in combination %}
                                                <span class="lotto-ball ball-{{ ((num-1)//10)*10+1 }}-{{ min(((num-1)//10+1)*10, 45) }}">{{ num }}</span>
                                            {% endfor %}
                                        </td>
                                    </tr>
                                    {% endfor %}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 지난주 당첨 결과 -->
        
        {% if not results %}
            <div class="row">
                <div class="col-12">
                    <div class="card">
                        <div class="card-body">
                            <p class="text-center">아직 당첨 결과가 없습니다. 매주 토요일 오후 10시에 당첨 결과를 확인합니다.</p>
                        </div>
                    </div>
                </div>
            </div>
        {% else %}
            {% for key, result in results %}
                <div class="row mb-3">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-header bg-warning text-dark">
                                <h4>{{ result.round }}회 ({{ result.date }}) 당첨 결과</h4>
                            </div>
                            <div class="card-body">
                                <div class="mb-2">
                                    <h5>당첨 번호</h5>
                                    <div>
                                        {% for num in result.winning_numbers %}
                                            <span class="lotto-ball ball-{{ ((num-1)//10)*10+1 }}-{{ min(((num-1)//10+1)*10, 45) }}">{{ num }}</span>
                                        {% endfor %}
                                        <span class="lotto-ball bonus">{{ result.bonus_number }}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            {% endfor %}
        {% endif %}
        
        <div class="footer">
            <p>&copy; 2025 로또 번호 분석 및 추천 서비스</p>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('refreshBtn').addEventListener('click', function() {
            // AJAX 요청으로 새로운 조합 가져오기
            fetch('/refresh-combinations')
                .then(response => response.text())
                .then(html => {
                    document.getElementById('combinations-container').innerHTML = html;
                });
        });
    </script>
</body>
</html>
        ''',
        
        'combinations_partial.html': '''
{% for combination in combinations %}
<tr>
    <td>행운 {{ loop.index }}</td>
    <td>
        {% for num in combination %}
            <span class="lotto-ball ball-{{ ((num-1)//10)*10+1 }}-{{ min(((num-1)//10+1)*10, 45) }}">{{ num }}</span>
        {% endfor %}
    </td>
</tr>
{% endfor %}
        '''
    }
    
    # 템플릿 파일 생성
    for filename, content in templates.items():
        filepath = os.path.join('templates', filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
    
    print("HTML 템플릿 파일이 생성되었습니다.")