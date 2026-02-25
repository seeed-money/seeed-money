import io  # 메모리 내에서 이진 데이터(이미지 등)를 다루기 위한 모듈

import matplotlib.pyplot as plt  # 그래프 시각화를 위한 라이브러리
import pandas as pd  # 데이터를 표 형태로 가공하기 위한 라이브러리
from django.core.files.base import ContentFile  # 메모리 데이터를 장고 파일 객체로 변환
from django.utils import timezone  # 장고의 시간대 설정을 반영한 현재 시간 가져오기

from transactions.models import Transaction

from .models import Analysis  # 분석 결과를 저장할 모델


class TransactionAnalyzer:
    def __init__(self, user, period_type, start_date, end_date):
        self.user = user  # 분석 대상 유저 객체 저장
        self.period_type = period_type  # 분석 주기 (매주/매월 등)
        self.start_date = start_date  # 분석 시작 날짜
        self.end_date = end_date  # 분석 종료 날짜

    def fetch_and_process_data(self):
        """데이터를 가져와서 입금/출금을 컬럼으로 분리"""
        # data = [
        #     {"transaction_at": "2026-02-01", "amount": 3000000, "transaction_type": "INCOME"},  # 월급
        #     {"transaction_at": "2026-02-01", "amount": 850000, "transaction_type": "EXPENSE"},  # 월세/공과금
        #     {"transaction_at": "2026-02-03", "amount": 45000, "transaction_type": "EXPENSE"},  # 식비
        #     {"transaction_at": "2026-02-08", "amount": 120000, "transaction_type": "EXPENSE"},  # 마트 장보기
        #     {"transaction_at": "2026-02-10", "amount": 50000, "transaction_type": "INCOME"},  # 중고판매 수입
        #     {"transaction_at": "2026-02-12", "amount": 30000, "transaction_type": "EXPENSE"},  # 교통비
        #     {"transaction_at": "2026-02-15", "amount": 500000, "transaction_type": "EXPENSE"},  # 경조사 또는 전자제품 구매
        #     {"transaction_at": "2026-02-17", "amount": 15000, "transaction_type": "EXPENSE"},  # 구독료
        #     {"transaction_at": "2026-02-20", "amount": 200000, "transaction_type": "INCOME"},  # 부업/성과급
        #     {"transaction_at": "2026-02-24", "amount": 60000, "transaction_type": "EXPENSE"},  # 외식
        #     {"transaction_at": "2026-02-27", "amount": 40000, "transaction_type": "EXPENSE"},  # 주유비
        #     {"transaction_at": "2026-02-28", "amount": 100000, "transaction_type": "EXPENSE"},  # 기타 쇼핑
        # ]
        # df = pd.DataFrame(data)

        # values()를 사용하여 리스트-딕셔너리 형태로 데이터를 뽑기
        queryset = Transaction.objects.filter(user=self.user, transaction_at__range=[self.start_date, self.end_date]).values("transaction_at", "amount", "transaction_type")

        # 쿼리셋을 리스트로 변환 후 데이터프레임 생성
        df = pd.DataFrame(list(queryset))

        if df.empty:
            return None

        # df["date"] = pd.to_datetime(df["transaction_at"])
        df["date"] = pd.to_datetime(df["transaction_at"]).dt.date  # 날짜형식만 보여주기

        # transaction_type별로 금액을 합산
        df = df.groupby(["date", "transaction_type"])["amount"].sum().unstack(fill_value=0).reset_index()

        # 한 종류만 있으면 에러예상하여 제로값 넣어주기
        if "INCOME" not in df.columns:
            df["INCOME"] = 0
        if "EXPENSE" not in df.columns:
            df["EXPENSE"] = 0

        return df

    def create_visualization(self, df):
        """입금(파란색)과 출금(빨간색)을 선 그래프로 시각화"""
        plt.figure(figsize=(10, 5))

        # 두 개의 선 그리기
        # plt.plot(df["date"], df["INCOME"], label="Income", color="blue", marker="o")
        # plt.plot(df["date"], df["EXPENSE"], label="Expense", color="red", marker="o")
        plt.plot(df["date"], df["INCOME"], label="Income", color="#4e73df", marker="o", linewidth=2)
        plt.plot(df["date"], df["EXPENSE"], label="Expense", color="#e74a3b", marker="o", linewidth=2)

        plt.title("Financial Analysis: Income vs Expense")
        plt.legend()  # 범례 표시
        plt.grid(True, linestyle=":", alpha=0.6)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        plt.close()
        return buffer

    def save_analysis(self):
        df = self.fetch_and_process_data()
        if df is None:
            return None

        chart_buffer = self.create_visualization(df)

        # 총합 금액보다 입금,출금 두 그래프로 보여줌
        total_income = df["INCOME"].sum()
        total_expense = df["EXPENSE"].sum()

        new_analysis = Analysis(
            user=self.user,
            period_type=self.period_type,
            start_date=self.start_date,
            end_date=self.end_date,
            description=f"분석 결과: 총 수입 {total_income}원, 총 지출 {total_expense}원",
        )

        file_name = f"chart_{self.user.id}_{timezone.now().strftime('%Y%m%d%H%M')}.png"
        new_analysis.result_image.save(file_name, ContentFile(chart_buffer.getvalue()), save=True)
        return new_analysis
