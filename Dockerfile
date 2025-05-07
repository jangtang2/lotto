FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# 데이터 디렉토리 생성
RUN mkdir -p data

# 환경 변수 설정
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# 포트 설정
EXPOSE 8080

# Gunicorn으로 실행
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]