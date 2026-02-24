# transactions/models.py
from django.conf import settings
from django.db import models


class Transaction(models.Model):
    TRANSACTION_TYPE = [
        ("INCOME", "수입"),
        ("EXPENSE", "지출"),
    ]

    # ⭐️ 1. 작성자(User) 연결: 내 데이터만 보기
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="transactions", verbose_name="작성자")

    # ⭐️2. account_id (FK) 계좌 연결
    account = models.ForeignKey(
        # 하나의 계좌에 여러개의 거래내역이 쌓일 수 있다
        "accounts.Account",
        # accounts앱의 Account모델
        on_delete=models.CASCADE,
        related_name="transactions",
        # Account쪽에서 역참조하면 transactions로불러라
        verbose_name="계좌ID",
        # 관리지 페이지에서는 필드 이름 '계좌ID'
    )
    # amount (거래금액)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="거래금액")
    # balance_after (거래후잔액)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="거래후잔액")
    # description (거래내역) 😂
    description = models.CharField(max_length=255, verbose_name="거래내역")
    # transaction_type (거래유형)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE, verbose_name="거래유형")
    # transaction_method (결제수단)
    transaction_method = models.CharField(max_length=20, verbose_name="결제수단")
    # transaction_at (거래일시) 😂
    transaction_at = models.DateTimeField(auto_now_add=True, verbose_name="거래일시")

    class Meta:
        db_table = "transaction_history"  # ERD 설계도 이름으로 지정
        verbose_name = "거래내역"
        verbose_name_plural = "거래내역 목록"

    def __str__(self):
        return f"{self.transaction_at} - {self.description} ({self.amount})"

    # ⭐️잔액 자동 업데이트 로직
    def save(self, *args, **kwargs):
        # 1. 거래 유형에 따라 잔액을 계산
        if self.transaction_type == "INCOME":  # 수입
            self.balance_after = self.account.balance + self.amount
        else:  # EXPENSE (지출)
            self.balance_after = self.account.balance - self.amount

        # 2. 계산된 balance_after를 실제 계좌(Account)에도 반영
        self.account.balance = self.balance_after
        self.account.save()

        # 3. 최종적으로 거래 내역(자신)을 저장
        super().save(*args, **kwargs)
