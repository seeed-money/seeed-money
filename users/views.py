from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CustomUser
from .serializers import UserRegisterSerializer, UserSerializer


# [Generic View] 회원가입: 단순 생성 로직에 최적
class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


# [APIView] 내 프로필: PK 없이 '나(request.user)'를 다루는 특수 로직에 적합
class MyProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# [ViewSet] 유저 관리: 목록 조회, 상세 보기, Soft Delete 등 관리 기능을 집합
class UserManagementViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # 관리자(grade>=2) 전용

    def get_queryset(self):
        # 삭제 완료 상태가 아닌 유저들만 반환
        return self.queryset.exclude(status=CustomUser.Status.DELETED)

    def perform_destroy(self, instance):
        # DELETE 요청 시 모델의 soft_delete 메서드 호출
        instance.soft_delete()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        """삭제 대기 유저 복구 액션: /users/management/{id}/restore/"""
        user = self.get_object()
        if user.status == CustomUser.Status.DELETING:
            user.undo_delete()
            return Response({"detail": "계정이 복구되었습니다."})
        return Response({"detail": "복구 가능한 상태가 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
