import os
from flask import Flask

# Flask 애플리케이션 생성
app = Flask(__name__)
app.secret_key = os.urandom(24)  # 세션 암호화를 위한 키

# Jinja2에 min 및 max 함수 추가
app.jinja_env.globals.update(min=min, max=max)

# 라우트 등록
from routes import register_routes
register_routes(app)

# 스케줄러 시작
from scheduler import start_scheduler
start_scheduler()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)