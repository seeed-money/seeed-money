from django.conf import settings
from django.db import models

from core.constants import ACCOUNT_TYPE, BANK_CODES


class Account(models.Model):
    """
    사용자의 계좌 정보를 저장하는 모델입니다.
    """

    # 1. 사용자 연결
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
        verbose_name="소유자",
    )

    # 2. 은행 정보 (constants.py의 BANK_CODES 사용)
    bank_code = models.CharField(max_length=3, choices=BANK_CODES, verbose_name="은행코드")

    # 3. 계좌 번호
    account_number = models.CharField(max_length=30, unique=True, verbose_name="계좌번호")

    # 4. 계좌 별명 (예: 급여 통장, 비상금)
    account_name = models.CharField(max_length=50, verbose_name="계좌별명")

    # 5. 계좌 유형 (constants.py의 ACCOUNT_TYPE 사용)
    # 입출금, 적금, 주식 등 파일에 정의된 값을 사용합니다.
    account_type = models.CharField(
        max_length=20, choices=ACCOUNT_TYPE, default="CHECKING", verbose_name="계좌유형"
    )

    # 6. 주 계좌 여부
    is_main = models.BooleanField(default=False, verbose_name="주계좌여부")

    # 7. 잔액
    balance = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="잔액")

    # 8. 생성 및 수정 일시
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일시")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        db_table = "accounts"
        verbose_name = "계좌"
        verbose_name_plural = "계좌 목록"

    def __str__(self):
        # get_bank_code_display()는 선택지(choices)의 한글명을 가져오는 장고 내장 함수임.
        return f"[{self.get_bank_code_display()}] {self.account_name}"
