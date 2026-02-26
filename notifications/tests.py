from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import Notification

User = get_user_model()


class NotificationIntegrationTests(APITestCase):
    def setUp(self):
        # CustomUser 모델에 맞춰 필드 구성
        # username 필드는 None이므로 제외하고, email을 기본 식별자로 사용합니다.
        self.user = User.objects.create_user(email="test@example.com", nickname="tester_nick", name="테스터", phone_number="01012345678", password="testpassword")
        self.client.force_authenticate(user=self.user)

    def test_unread_notification_list(self):
        """미확인 알림 리스트 조회 테스트"""
        # 테스트용 알림 생성
        Notification.objects.create(user=self.user, message="테스트 알림입니다", is_read=False)

        url = reverse("unread-notifications")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # 응답 데이터가 리스트인지, 생성한 알림이 포함되어 있는지 확인
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["message"], "테스트 알림입니다")

    def test_notification_read_workflow(self):
        """알림을 읽음 처리하고 리스트에서 사라지는지 테스트"""
        # 1. 알림 생성
        noti = Notification.objects.create(user=self.user, message="읽기 전 알림")

        # 2. 읽음 처리 API 호출 (PATCH)
        read_url = reverse("read-notification", kwargs={"pk": noti.pk})
        response = self.client.patch(read_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 3. 다시 미확인 리스트 조회 시 결과가 0개여야 함
        list_url = reverse("unread-notifications")
        list_response = self.client.get(list_url)
        self.assertEqual(len(list_response.data), 0)

    def test_other_user_notification_access(self):
        """다른 유저의 알림을 수정하려 할 때 403 에러가 나는지 테스트"""
        # 다른 유저 생성 (이메일과 닉네임은 unique=True이므로 다르게 설정)
        other_user = User.objects.create_user(email="other@example.com", nickname="other_nick", name="다른이", phone_number="01099998888", password="password123")
        other_noti = Notification.objects.create(user=other_user, message="남의 알림")

        url = reverse("read-notification", kwargs={"pk": other_noti.pk})
        response = self.client.patch(url)

        # 권한 없음(403) 확인
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
