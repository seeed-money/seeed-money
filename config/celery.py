import os

from celery import Celery

# 1. 장고의 설정 파일(settings.py)을 가리킵니다.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 2. Celery 앱 인스턴스를 생성합니다. (이름은 프로젝트명으로)
app = Celery("seeed_money")

# 3. 'CELERY_'로 시작하는 설정들을 settings.py에서 읽어옵니다.
app.config_from_object("django.conf:settings", namespace="CELERY")

# 4. 각 앱(accounts, analysis 등) 안에 있는 tasks.py를 자동으로 찾습니다.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")


# 5. [추가] 스케줄링 작업 등록 (방법 B)
app.conf.beat_schedule = {
    "analysis-every-minute": {
        "task": "analysis.tasks.analyze_spending_habi",
        "schedule": 3600.0,  # 1시마다 실행
    },
}
