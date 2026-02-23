from rest_framework import permissions, viewsets

from .models import Account
from .serializers import AccountSerializer


class AccountViewSet(viewsets.ModelViewSet):
    # 데이터 변환기(Serializer) 설정
    serializer_class = AccountSerializer
    # 인증된(로그인한) 사용자만 이 API를 사용할 수 있도록 권한을 제한합니다.
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # 로그인한 사용자가 본인의 계좌만 볼 수 있도록 데이터 범위를 제한합니다.
        return Account.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # 계좌를 생성할 때, 현재 API를 호출한 유저 정보(self.request.user)를 자동으로 저장합니다.
        serializer.save(user=self.request.user)
