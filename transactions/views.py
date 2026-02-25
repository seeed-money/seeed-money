from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import permissions, viewsets

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    # 인증된 사용자만 접근 가능하도록 설정 (로그인 안 하면 안 보임)
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(parameters=[OpenApiParameter(name="account", description="필터링할 계좌의 ID (숫자)", required=False, type=int)])
    def list(self, request, *args, **kwargs):
        # 기본 list 기능을 그대로 쓰겠다!
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        # ⭐️1. 내 데이터만 보기 기능:현재 로그인한 유저(self.request.user)
        user = self.request.user

        # 관리자(is_staff)라면 전체 데이터를, 일반 유저라면 본인 데이터만 가져옴
        if user.is_staff:
            queryset = Transaction.objects.all()
        else:
            queryset = Transaction.objects.filter(user=user)

        # ⭐️ 특정 계좌의 거래 내역만 필터링 (URL에 ?account=아이디 가 있을 경우)
        # 예: /api/transactions/?account=5 요청 시 5번 계좌 내역만 필터링됨
        account_id = self.request.query_params.get("account")
        if account_id:
            queryset = queryset.filter(account_id=account_id)

        return queryset.order_by("-transaction_at")

    def perform_create(self, serializer):
        # ⭐️2.현재 로그인된 유저 정보를 모델의 user 필드에 자동으로 넣어줌
        serializer.save(user=self.request.user)
