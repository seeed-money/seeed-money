from django.conf import settings
from django.db import models

from core.constants import ACCOUNT_TYPE, BANK_CODES


class Account(models.Model):
    # 1. 사용자 연결: 유저 한 명이 여러 계좌를 가질 수 있도록 설정합니다.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="accounts",
        verbose_name="소유자",
    )
    # 2. 은행 정보: constants.py에서 가져온 은행 코드 리스트를 선택지로 사용합니다.
    bank_code = models.CharField(max_length=3, choices=BANK_CODES, verbose_name="은행코드")
    # 3. 계좌 번호: 시스템 전체에서 유일해야 하며 최대 30자까지 허용합니다.
    account_number = models.CharField(max_length=30, unique=True, verbose_name="계좌번호")
    # 4. 계좌 별명: 사용자가 식별하기 쉬운 이름(예: 비상금)을 입력받습니다.
    account_name = models.CharField(max_length=50, verbose_name="계좌별명")
    # 5. 계좌 유형: 입출금, 적금 등의 유형을 저장하며 기본값은 보통예금입니다.
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE, default="CHECKING", verbose_name="계좌유형")
    # 6. 주 계좌 여부: 해당 계좌가 사용자의 대표 계좌인지 체크하는 필드입니다.
    is_main = models.BooleanField(default=False, verbose_name="주계좌여부")
    # 7. 잔액: 최대 15자리 숫자를 소수점 없이 저장하며 기본값은 0원입니다.
    balance = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="잔액")
    # 8. 등록 일시: 데이터가 처음 생성될 때의 시간이 자동으로 저장됩니다.
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="등록일시")
    # 9. 수정 일시: 데이터가 업데이트될 때마다 현재 시간이 자동으로 갱신됩니다.
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일시")

    class Meta:
        # 데이터베이스에 생성될 테이블의 이름
        db_table = "accounts"
        # 관리자 페이지 등에서 보여질 모델의 단수형 이름
        verbose_name = "계좌"
        # 관리자 페이지 등에서 보여질 모델의 복수형 이름
        verbose_name_plural = "계좌 목록"
        # 동일한 유저가 같은 은행의 같은 계좌번호를 중복 생성하는 것을 방지함
        unique_together = ("user", "bank_code", "account_number")

    def __str__(self):
        # 객체를 출력할 때 [은행이름] 계좌별명 형태로 보임
        return f"[{self.get_bank_code_display()}] {self.account_name}"

    def save(self, *args, **kwargs):
        # 만약 현재 계좌를 주 계좌로 설정하여 저장하려고 한다면 로직을 실행합니다.
        if self.is_main:
            # 같은 유저의 기존 주 계좌들을 모두 찾아서 주 계좌 설정(is_main)을 해제합니다.
            Account.objects.filter(user=self.user, is_main=True).exclude(id=self.id).update(is_main=False)
        # 최종적으로 부모 클래스의 저장 기능을 호출하여 실제 DB에 반영합니다.
        super().save(*args, **kwargs)
