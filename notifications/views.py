from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


# 미확인 알림 리스트
class UnreadNotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]  # 로그인한 유저만 접근 가능

    def get_queryset(self):
        # 현재 로그인한 유저의 알림 중 읽지 않은(is_read=False) 것만 필터링
        return Notification.objects.filter(user=self.request.user, is_read=False).order_by("-created_at")  # 최신순 정렬


# 알림 읽음 처리
class NotificationReadView(generics.UpdateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"  # URL 파라미터로 받을 필드명 (기본값 pk)

    # PATCH 메서드만 허용하도록 명시
    http_method_names = ["patch"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # 권한 체크: 남의 알림을 읽음 처리하면 안 되므로
        if instance.user != request.user:
            return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

        instance.is_read = True
        instance.save()

        return Response({"message": f"알림 {instance.notification_id}번을 읽음 처리했습니다.", "is_read": instance.is_read}, status=status.HTTP_200_OK)


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 현재 로그인한 유저의 읽지 않은 알림들만 필터링
        unread_notifications = Notification.objects.filter(user=request.user, is_read=False)

        # 한 번에 업데이트 (DB에서 SQL로 바로 처리되어 매우 빠름)
        updated_count = unread_notifications.update(is_read=True)

        return Response({"message": f"{updated_count}개의 알림을 모두 읽음 처리했습니다."}, status=status.HTTP_200_OK)
