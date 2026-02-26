from django.conf import settings
from django.db import models


class Notification(models.Model):
    notification_id = models.AutoField(primary_key=True)

    # user_id (외래키 연결)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")

    # 메시지 (TEXT)
    message = models.TextField()

    # 읽음여부 (BOOLEAN, 기본값은 안읽음(False))
    is_read = models.BooleanField(default=False)

    # 생성일 (DATETIME, 생성 시 자동 저장)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "notifications"  # ERD에 명시된 테이블 이름
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.user.username}] {self.message[:20]}"
