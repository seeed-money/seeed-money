from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    ordering = ("email",)

    # 목록 뷰 설정
    list_display = ("email", "nickname", "name", "is_staff")

    # 상세 수정 페이지 레이아웃
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("개인 정보", {"fields": ("nickname", "name", "phone_number")}),
        ("권한", {"fields": ("is_active", "is_staff", "is_superuser", "grade", "status")}),
    )

    # 유저 추가(Add) 페이지 레이아웃
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "nickname",
                    "name",
                    "phone_number",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    # 기타 필수 설정
    filter_horizontal = ()
    search_fields = ("email", "nickname", "name")
    readonly_fields = ("created_at", "updated_at", "deleted_at")
