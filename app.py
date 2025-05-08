import os
from flask import Flask

# Flask 애플리케이션 생성
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # 환경 변수에서 시크릿 키 가져오기

# Jinja2에 min 및 max 함수 추가
app.jinja_env.globals.update(min=min, max=max)

# 라우트 등록
from routes import register_routes
register_routes(app)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)