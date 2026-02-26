import logging
import os

import google.generativeai as genai
from celery import shared_task
from django.db.models import Sum
from django.utils import timezone
from dotenv import load_dotenv

from transactions.models import Transaction

load_dotenv()
logger = logging.getLogger(__name__)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


@shared_task(name="analysis.tasks.analyze_spending_habit")
def analyze_spending_habit():
    logger.info("🚀워렌버핏 빙의한 AI의 소비 분석 시작...")

    try:
        # 1. 이번 달 범위 설정
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        # 2. 이번 달 지출(EXPENSE) 내역 가져오기
        # (현재는 모든 사용자를 대상으로 하지만, 나중에 특정 사용자별로 루프를 돌릴 수도 있습니다)
        expenses = Transaction.objects.filter(transaction_type="EXPENSE", transaction_at__gte=start_of_month)

        if not expenses.exists():
            logger.info("ℹ️ 이번 달 지출 내역이 없어 분석을 건너뜁니다.")
            return "No data"

        # 3. 데이터 요약 (AI에게 전달할 텍스트 만들기)
        # 예: "식당 (10,000원), 편의점 (5,000원)..."
        expense_list = []
        for ex in expenses:
            expense_list.append(f"{ex.description} ({int(ex.amount)}원)")

        total_amount = expenses.aggregate(Sum("amount"))["amount__sum"] or 0
        data_str = ", ".join(expense_list)

        # 4. Gemini 모델 설정
        model = genai.GenerativeModel("models/gemini-flash-latest")

        prompt = (
            "너는 사용자의 가계부 내역을 분석하는 냉철한 자산관리 전문가야. "
            f"이번 달 지출 내역들: [{data_str}]. "
            f"총 지출 금액: {int(total_amount)}원. "
            "이 내역을 보고 소비 습관에 대해 아주 짧고 뼈 때리는 조언을 한 줄로 해줘."
        )

        # 5. AI 답변 생성
        response = model.generate_content(prompt)
        ai_advice = response.text.strip()

        logger.info(f"😎분석 완료! 이번 달 총 지출: {int(total_amount)}원")
        logger.info(f"😁AI의 조언: {ai_advice}")

        return ai_advice

    except Exception as e:
        logger.error(f"❌ 데이터 분석 중 에러 발생: {str(e)}")
        return f"Error: {str(e)}"
