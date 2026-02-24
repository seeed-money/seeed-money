from rest_framework import permissions, viewsets

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer
    # 인증된 사용자만 접근 가능하도록 설정 (로그인 안 하면 안 보임)
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # ⭐️1. 내 데이터만 보기 기능:현재 로그인한 유저(self.request.user)
        return Transaction.objects.filter(user=self.request.user).order_by("-transaction_at")

    def perform_create(self, serializer):
        # ⭐️2.현재 로그인된 유저 정보를 모델의 user 필드에 자동으로 넣어줍니다.
        serializer.save(user=self.request.user)
