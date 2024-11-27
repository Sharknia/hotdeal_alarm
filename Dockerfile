# 베이스 이미지
FROM python:3.9-slim

# Poetry 설치
RUN pip install poetry

# 작업 디렉토리 설정
WORKDIR /app

# Poetry 프로젝트 파일 복사
COPY pyproject.toml poetry.lock ./

# 의존성 설치
RUN poetry install --no-root

# 코드 복사
COPY . .

# 기본 실행 명령어
CMD ["poetry", "run", "python", "main.py"]
