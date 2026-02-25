from .celery import app as celery_app

__all__ = ("celery_app",)

# 장고가 켜질 때 Celery 설정도 같이 켜지도록 연결
