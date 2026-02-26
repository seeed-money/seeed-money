## 1. uv 설치 이미지를 별칭으로 설정
#FROM ghcr.io/astral-sh/uv:latest AS uv_bin
#
## 2. 실제 Python 실행 이미지
#FROM python:3.12-slim
#
## uv 바이너리 복사
#COPY --from=uv_bin /uv /uvx /bin/
#
## 작업 디렉토리 설정
#WORKDIR /app
#
## 의존성 파일 복사 및 설치 (캐싱 활용)
#COPY pyproject.toml uv.lock ./
#RUN uv sync --frozen --no-cache
#
## 소스 코드 복사
#COPY . .
#
## uv 환경의 가상환경(venv)을 PATH에 추가
#ENV PATH="/app/.venv/bin:$PATH"
#
## 실행 명령
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

#파이썬 베이스 이미지 선택
FROM python:3.12

#uv 설치 (공식 가이드 권장 방식)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

#작업 디렉토리 설정
WORKDIR /app

#의존성 파일 먼저 복사 (캐싱 효율을 위해)
COPY pyproject.toml uv.lock ./

#의존성 설치
#--frozen: uv.lock 파일과 일치하는지 확인
#--no-install-project: 앱 코드를 복사하기 전에 라이브러리만 먼저 설치 (빌드 속도 향상)
RUN uv sync --no-cache

#나머지 소스 코드 복사
COPY . .

#(선택) 환경 변수 설정: uv가 생성한 가상환경의 bin을 PATH에 추가
ENV PATH="/app/.venv/bin:$PATH"

#서버 실행 명령어
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]