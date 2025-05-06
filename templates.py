import os

def create_templates():
    """기본 HTML 템플릿 파일 생성"""
    templates = {
        'index.html': '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>로또 번호 분석 및 추천</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            padding-bottom: 50px;
        }
        .jumbotron {
            background-color: #007bff;
            color: white;
            padding: 2rem;
            margin-bottom: 2rem;
            border-radius: 0.3rem;
        }
        .card {
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.3s;
        }
        .card:hover {
            transform: translateY(-5px);
        }
        .lotto-ball {
            display: inline-block;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            color: white;
            font-weight: bold;
            text-align: center;
            line-height: 40px;
            margin: 0 5px;
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
            margin-top: 30px;
            padding: 20px 0;
            background-color: #f1f1f1;
            text-align: center;
        }
        .match-count {
            font-size: 1.2rem;
            font-weight: bold;
        }
        .match-1, .match-2 { color: #6c757d; } /* 미당첨 */
        .match-3 { color: #28a745; } /* 5등 */
        .match-4 { color: #007bff; } /* 4등 */
        .match-5 { color: #fd7e14; } /* 3등 */
        .match-5bonus { color: #dc3545; } /* 2등 */
        .match-6 { color: #9c27b0; } /* 1등 */
        .section-title {
            border-left: 5px solid #007bff;
            padding-left: 10px;
            margin: 30px 0 20px;
        }
    </style>
</head>
<body>
    <div class="jumbotron text-center">
        <h1>언젠간 될지어다</h1>
        <p>통계 기반 로또 번호 분석 및 추천 서비스</p>
    </div>
    
    <div class="container">
        <!-- 추천 번호 -->
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-success text-white">
                        <h4>로또 번호 추천</h4>
                    </div>
                    <div class="card-body">
                        <div class="mb-3">
                            <p><strong>추첨일:</strong> {{ target_date }}</p>
                        </div>
                        
                        <div class="table-responsive">
                            <table class="table table-striped table-hover">
                                <thead>
                                    <tr>
                                        <th>번호</th>
                                        <th>추천 조합</th>
                                    </tr>
                                </thead>
                                <tbody id="combinations-container">
                                    {% for combination in combinations %}
                                    <tr>
                                        <td>조합 {{ loop.index }}</td>
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
        <h2 class="section-title">지난주 당첨 결과</h2>
        
        {% if not results %}
            <div class="row">
                <div class="col-md-12">
                    <div class="card">
                        <div class="card-body">
                            <p class="text-center">아직 당첨 결과가 없습니다.\n 매주 토요일 오후 10시에 당첨 결과를 확인합니다.</p>
                        </div>
                    </div>
                </div>
            </div>
        {% else %}
            {% for key, result in results %}
                <div class="row mb-4">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-header bg-warning text-dark">
                                <h4>{{ result.round }}회 ({{ result.date }}) 당첨 결과</h4>
                            </div>
                            <div class="card-body">
                                <div class="mb-3">
                                    <h5>당첨 번호</h5>
                                    <div>
                                        {% for num in result.winning_numbers %}
                                            <span class="lotto-ball ball-{{ ((num-1)//10)*10+1 }}-{{ min(((num-1)//10+1)*10, 45) }}">{{ num }}</span>
                                        {% endfor %}
                                        <span class="lotto-ball bonus">{{ result.bonus_number }}</span>
                                    </div>
                                </div>
                                
                                <div class="row mb-3">
                                    <div class="col-md-12">
                                        <h5>추천 번호 당첨 통계</h5>
                                        <div class="table-responsive">
                                            <table class="table table-bordered">
                                                <thead class="table-light">
                                                    <tr>
                                                        <th>등수</th>
                                                        <th>일치 개수</th>
                                                        <th>비율</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td>1등</td>
                                                        <td>6개 일치</td>
                                                        
                                                        <td>{{ (result.match_counts['6'] / result.total_combinations * 100)|round(2) }}%</td>
                                                    </tr>
                                                    <tr>
                                                        <td>2등</td>
                                                        <td>5개 + 보너스</td>
                                                        
                                                        <td>{{ (result.match_counts['5+bonus'] / result.total_combinations * 100)|round(2) }}%</td>
                                                    </tr>
                                                    <tr>
                                                        <td>3등</td>
                                                        <td>5개 일치</td>
                                                       
                                                        <td>{{ (result.match_counts['5'] / result.total_combinations * 100)|round(2) }}%</td>
                                                    </tr>
                                                    <tr>
                                                        <td>4등</td>
                                                        <td>4개 일치</td>
                                                        
                                                        <td>{{ (result.match_counts['4'] / result.total_combinations * 100)|round(2) }}%</td>
                                                    </tr>
                                                    <tr>
                                                        <td>5등</td>
                                                        <td>3개 일치</td>
                                                        
                                                        <td>{{ (result.match_counts['3'] / result.total_combinations * 100)|round(2) }}%</td>
                                                    </tr>
                                                    <tr>
                                                        <td colspan="2">미당첨 (2개 이하)</td>
                                                        
                                                        <td>{{ ((result.match_counts['2'] + result.match_counts['1'] + result.match_counts['0']) / result.total_combinations * 100)|round(2) }}%</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                                
                                {% if result.matched_combinations %}
                                    <div class="row">
                                        <div class="col-md-12">
                                            <h5>당첨된 추천 번호</h5>
                                            <div class="table-responsive">
                                                <table class="table table-striped">
                                                    <thead>
                                                        <tr>
                                                            <th>번호 조합</th>
                                                            <th>일치 개수</th>
                                                            <th>등수</th>
                                                            <th>일치한 번호</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        {% for index, combo in result.matched_combinations.items() %}
                                                            <tr>
                                                                <td>
                                                                    {% for num in combo.combination %}
                                                                        <span class="lotto-ball ball-{{ ((num-1)//10)*10+1 }}-{{ min(((num-1)//10+1)*10, 45) }}">{{ num }}</span>
                                                                    {% endfor %}
                                                                </td>
                                                                <td>
                                                                    {% if combo.category == '6' %}
                                                                        <span class="match-6">6개 일치</span>
                                                                    {% elif combo.category == '5+bonus' %}
                                                                        <span class="match-5bonus">5개 + 보너스</span>
                                                                    {% else %}
                                                                        <span class="match-{{ combo.category }}">{{ combo.category }}개 일치</span>
                                                                    {% endif %}
                                                                </td>
                                                                <td>
                                                                    {% if combo.category == '6' %}
                                                                        <strong>1등</strong>
                                                                    {% elif combo.category == '5+bonus' %}
                                                                        <strong>2등</strong>
                                                                    {% elif combo.category == '5' %}
                                                                        <strong>3등</strong>
                                                                    {% elif combo.category == '4' %}
                                                                        <strong>4등</strong>
                                                                    {% elif combo.category == '3' %}
                                                                        <strong>5등</strong>
                                                                    {% else %}
                                                                        -
                                                                    {% endif %}
                                                                </td>
                                                                <td>
                                                                    {% for num in combo.matched %}
                                                                        <span class="lotto-ball ball-{{ ((num-1)//10)*10+1 }}-{{ min(((num-1)//10+1)*10, 45) }}">{{ num }}</span>
                                                                    {% endfor %}
                                                                    {% if combo.bonus_matched %}
                                                                        <span class="lotto-ball bonus">{{ result.bonus_number }}</span>
                                                                    {% endif %}
                                                                </td>
                                                            </tr>
                                                        {% endfor %}
                                                    </tbody>
                                                </table>
                                            </div>
                                        </div>
                                    </div>
                                {% else %}
                                    <div class="alert alert-info">
                                        이번 회차에는 3개 이상 일치하는 번호가 없었습니다.
                                    </div>
                                {% endif %}
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
    <td>조합 #{{ loop.index }}</td>
    <td>
        {% for num in combination %}
            <span class="lotto-ball ball-{{ ((num-1)//10)*10+1 }}-{{ min(((num-1)//10+1)*10, 45) }}">{{ num }}</span>
        {% endfor %}
    </td>
</tr>
{% endfor %}
        ''',
        
        'nfc_setup.html': '''
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NFC 태그 설정</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/css/bootstrap.min.css">
    <style>
        body {
            background-color: #f8f9fa;
            padding-bottom: 50px;
        }
        .jumbotron {
            background-color: #0dcaf0;
            color: white;
            padding: 2rem;
            margin-bottom: 2rem;
            border-radius: 0.3rem;
        }
        .card {
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .footer {
            margin-top: 30px;
            padding: 20px 0;
            background-color: #f1f1f1;
            text-align: center;
        }
        .nfc-info {
            background-color: #e9f7fb;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="jumbotron text-center">
        <h1>NFC 태그 설정</h1>
        <p>NFC 태그를 통한 간편 접근 설정</p>
    </div>
    
    <div class="container">
        <div class="row mb-4">
            <div class="col-md-12">
                <a href="/" class="btn btn-secondary mb-3">메인으로 돌아가기</a>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h4>NFC 태그 설정 안내</h4>
                    </div>
                    <div class="card-body">
                        <div class="nfc-info">
                            <h5>NFC 태그란?</h5>
                            <p>NFC(Near Field Communication) 태그는 스마트폰을 태그에 가까이 대면 
                            특정 동작을 수행하도록 하는 기술입니다. 이를 통해 웹사이트에 쉽게 접근할 수 있습니다.</p>
                        </div>
                        
                        <h5>태그 설정 방법</h5>
                        <ol>
                            <li>NFC 태그를 구입합니다. (온라인 쇼핑몰에서 쉽게 구매 가능)</li>
                            <li>아래에서 접근하고 싶은 페이지를 선택합니다.</li>
                            <li>생성된 URL을 NFC 태그 기록 앱을 사용하여 태그에 기록합니다.</li>
                            <li>태그에 스마트폰을 가까이 대면 해당 페이지로 바로 접근할 수 있습니다.</li>
                        </ol>
                        
                        <form id="nfcForm" class="mt-4">
                            <div class="mb-3">
                                <label for="baseUrl" class="form-label">사이트 기본 URL</label>
                                <input type="text" class="form-control" id="baseUrl" 
                                       placeholder="https://yourdomain.com/" required>
                                <div class="form-text">호스팅된 사이트의 URL을 입력하세요.</div>
                            </div>
                            
                            <div class="mb-3">
                                <label for="accessType" class="form-label">접근할 페이지</label>
                                <select class="form-select" id="accessType" required>
                                    <option value="">메인 페이지</option>
                                </select>
                                <div class="form-text">NFC 태그로 접근할 페이지를 선택하세요.</div>
                            </div>
                            
                            <button type="submit" class="btn btn-info">NFC 데이터 생성</button>
                        </form>
                        
                        <div id="nfcResult" class="mt-4" style="display: none;">
                            <h5>NFC 태그 데이터</h5>
                            <div class="card">
                                <div class="card-body">
                                    <p><strong>URL:</strong> <span id="resultUrl"></span></p>
                                    <p><strong>안드로이드 인텐트:</strong> <span id="resultIntent"></span></p>
                                    <p><strong>설명:</strong> <span id="resultDesc"></span></p>
                                    <button id="copyUrlBtn" class="btn btn-sm btn-outline-primary">URL 복사</button>
                                    <button id="copyIntentBtn" class="btn btn-sm btn-outline-secondary">인텐트 복사</button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-12">
                <div class="card">
                    <div class="card-header bg-light">
                        <h4>NFC 태그 사용 팁</h4>
                    </div>
                    <div class="card-body">
                        <ul>
                            <li>태그는 금속 표면에 부착하면 인식률이 떨어질 수 있습니다.</li>
                            <li>스마트폰 설정에서 NFC 기능이 활성화되어 있어야 합니다.</li>
                            <li>태그를 스마트폰 뒷면 중앙에 가까이 대면 가장 잘 인식됩니다.</li>
                            <li>안드로이드 사용자는 'NFC Tools'와 같은 앱을 사용하여 태그를 기록할 수 있습니다.</li>
                            <li>iOS 사용자는 'NFC TagWriter by NXP'와 같은 앱을 사용할 수 있습니다.</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>&copy; 2025 로또 번호 분석 및 추천 서비스</p>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.3.0/js/bootstrap.bundle.min.js"></script>
    <script>
        document.getElementById('nfcForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            // 입력값 가져오기
            const baseUrl = document.getElementById('baseUrl').value.trim();
            const accessType = document.getElementById('accessType').value;
            
            // 기본 URL 형식 확인
            let formattedBaseUrl = baseUrl;
            if (formattedBaseUrl && !formattedBaseUrl.endsWith('/')) {
                formattedBaseUrl += '/';
            }
            
            // AJAX 요청
            fetch('/generate-nfc-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `base_url=${encodeURIComponent(formattedBaseUrl)}&access_type=${encodeURIComponent(accessType)}`
            })
            .then(response => response.json())
            .then(data => {
                // 결과 표시
                document.getElementById('resultUrl').textContent = data.url;
                document.getElementById('resultIntent').textContent = data.android_intent;
                document.getElementById('resultDesc').textContent = data.description;
                document.getElementById('nfcResult').style.display = 'block';
                
                // 복사 버튼 설정
                document.getElementById('copyUrlBtn').onclick = function() {
                    navigator.clipboard.writeText(data.url);
                    alert('URL이 클립보드에 복사되었습니다.');
                };
                
                document.getElementById('copyIntentBtn').onclick = function() {
                    navigator.clipboard.writeText(data.android_intent);
                    alert('안드로이드 인텐트가 클립보드에 복사되었습니다.');
                };
            })
            .catch(error => {
                console.error('Error:', error);
                alert('NFC 데이터 생성 중 오류가 발생했습니다.');
            });
        });
    </script>
</body>
</html>
        '''
    }
    
    # 템플릿 파일 생성
    for filename, content in templates.items():
        filepath = os.path.join('templates', filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(content)
    
    print("HTML 템플릿 파일이 생성되었습니다.")