from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    # 은행 이름, 계좌 유형 이름(보통예금, 주식계좌등)
    bank_name = serializers.CharField(source="get_bank_code_display", read_only=True)
    type_name = serializers.CharField(source="get_account_type_display", read_only=True)

    class Meta:
        model = Account
        # 사용자에게 보여주거나 입력받을 기본 필드 목록
        fields = [
            "id",
            "user",
            "bank_code",
            "bank_name",
            "account_number",
            "account_name",
            "account_type",
            "type_name",
            "is_main",
            "balance",
            "created_at",
        ]

        # 불변의 사실 기록하는 컬럼 -> 수정 불가능하게 관리
        read_only_fields = ["id", "created_at", "user"]

    def __init__(self, *args, **kwargs):
        # ⭐️ 1. 뷰(View)에서 전달된 request 정보를 가져옵니다.
        request = kwargs.get("context", {}).get("request")

        super(AccountSerializer, self).__init__(*args, **kwargs)

        # ⭐️ 2. 로그인한 유저가 관리자(is_staff)라면 'user_email' 필드를 동적으로 추가합니다.
        if request and request.user and request.user.is_staff:
            self.fields["user_email"] = serializers.ReadOnlyField(source="user.email")

    def create(self, validated_data):
        # 현재 로그인한 유저를 자동으로 할당하기 위해 view에서 유저 정보를 넘겨받음
        return Account.objects.create(**validated_data)

    def validate_balance(self, value):
        # 계좌 개설 시 잔액이 0원 미만이 될 수 없도록 검사 로직을 추가
        if value < 0:
            # 잔액이 0보다 작으면 에러 메시지
            raise serializers.ValidationError("초기 잔액은 0원 이상이어야 합니다.")
        # 검사가 통과된 값을 반환
        return value
