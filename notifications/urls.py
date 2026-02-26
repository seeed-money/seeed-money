from django.urls import path

from .views import NotificationReadAllView, NotificationReadView, UnreadNotificationListView

urlpatterns = [
    path("unread/", UnreadNotificationListView.as_view(), name="unread-notifications"),
    path("<int:pk>/read/", NotificationReadView.as_view(), name="read-notification"),
    path("read-all/", NotificationReadAllView.as_view(), name="read-all-notifications"),
]
