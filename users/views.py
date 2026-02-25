from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import CustomUser
from .permissions import IsSelf
from .serializers import LoginSerializer, UserRegisterSerializer, UserSerializer


# 회원가입(POST)
class UserRegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]

    # 회원가입 직후 로직을 넣는 곳
    # def perform_create(self, serializer):
    #     ...


# 회원조회 및 수정(GET,PUT)
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


# 회원 로그인(POST)
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # JWT 토큰 생성
            refresh = RefreshToken.for_user(user)

            return Response({"refresh": str(refresh), "access": str(refresh.access_token), "user": {"email": user.email, "nickname": user.nickname, "grade": user.grade}}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 회원삭제(DELETE)
# ListModelMixin: 목록조회
# RetrieveModelMixin: 상세조회
# DestroyModelMixin: 삭제
# GenericViewSet: 위의 3기능만을 사용하도록 조성한 환경
# ModelViewSet: 모든 기능을 가진 환경
class UserManagementViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser | IsSelf]  # 관리자이거나 본인이거나

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return self.queryset.exclude(status=CustomUser.Status.DELETED)
        return self.queryset.filter(id=user.id)

    def perform_destroy(self, instance):
        # DELETE 요청 시 모델의 soft_delete 메서드 호출
        instance.soft_delete()

    @action(detail=True, methods=["post"], url_path="restore")
    def restore(self, request, pk=None):
        """삭제 대기 유저 복구 액션: /users/management/{pk}/restore/"""
        user = self.get_object()
        if user.status == CustomUser.Status.DELETING:
            user.undo_delete()
            return Response({"detail": "계정이 복구되었습니다."})
        return Response({"detail": "복구 가능한 상태가 아닙니다."}, status=status.HTTP_400_BAD_REQUEST)
