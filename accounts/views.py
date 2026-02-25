from drf_spectacular.utils import OpenApiParameter, extend_schema  # ⭐️ Swagger 설정을 위해 추가
from rest_framework import permissions, viewsets

from .models import Account
from .serializers import AccountSerializer


class AccountViewSet(viewsets.ModelViewSet):
    # 데이터 변환기(Serializer) 설정
    serializer_class = AccountSerializer
    # 인증된(로그인한) 사용자만 이 API를 사용할 수 있도록 권한을 제한
    permission_classes = [permissions.IsAuthenticated]

    # ⭐️ Swagger에서 관리자가 이메일로 검색할 수 있는 입력창
    @extend_schema(parameters=[OpenApiParameter(name="email", description="검색할 유저의 이메일 일부 (관리자 전용)", required=False, type=str)])
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        # ⭐️ 관리자(is_staff)라면 전체 계좌를, 일반 유저라면 본인 계좌만 가져오게
        user = self.request.user

        if user.is_staff:
            queryset = Account.objects.all()

            # 🔍 이메일 검색 파라미터 확인 (?email=...)
            email_query = self.request.query_params.get("email")
            if email_query:
                # 이메일에 해당 글자가 포함된 유저의 계좌만 필터링 (대소문자 무시)
                queryset = queryset.filter(user__email__icontains=email_query)

            return queryset

        # 로그인한 사용자가 본인의 계좌만 볼 수 있도록 데이터 범위를 제한
        return Account.objects.filter(user=user)

    def perform_create(self, serializer):
        # 계좌를 생성할 때, 현재 API를 호출한 유저 정보(self.request.user)를 자동으로 저장
        serializer.save(user=self.request.user)
