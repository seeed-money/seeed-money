from rest_framework import permissions


class IsSelf(permissions.BasePermission):
    """
    객체의 소유자(본인)만 접근을 허용하는 권한
    """

    def has_object_permission(self, request, view, obj):
        # 로그인한 유저와 조회/수정/삭제하려는 객체(유저)가 일치하는지 확인
        return obj == request.user
