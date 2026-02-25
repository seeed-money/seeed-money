# analysis/tasks.py
import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def analyze_spending_habit():
    logger.info("소비 패턴 분석 시작...")

    # 여기에 실제 분석 로직 (DB 쿼리 등)이 들어갑니다.
    # 예: Transaction.objects.filter(...)

    logger.info("소비 패턴 분석 완료!")
    return "Analysis Completed"
