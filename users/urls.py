from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import LoginView, MyProfileView, UserManagementViewSet, UserRegisterView

# 1. ViewSet을 위한 Router 설정 (관리자용)
router = DefaultRouter()
router.register(r"management", UserManagementViewSet, basename="user-management")

urlpatterns = [
    # 회원가입 (POST /users/register/)
    path("register/", UserRegisterView.as_view(), name="user-register"),
    # 내 프로필 조회 및 수정 (GET, PATCH /users/profile/)
    path("profile/", MyProfileView.as_view(), name="user-profile"),
    path("login/", LoginView.as_view(), name="user-login"),
    # [관리자,본인 전용]
    # /users/management/ (GET: 목록조회)
    # /users/management/{pk}/ (GET: 상세조회, DELETE: 소프트삭제)
    # /users/management/{pk}/restore/ (POST: 복구)
    path("", include(router.urls)),
]
