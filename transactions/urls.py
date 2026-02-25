from django.urls import include, path
from rest_framework.routers import DefaultRouter

# 얘가 {id}경로 자동으로 만들어줌
from .views import TransactionViewSet

router = DefaultRouter()
router.register(r"history", TransactionViewSet, basename="transaction")  # /api/transactions/history/ 주소 생성

urlpatterns = [
    path("", include(router.urls)),
]
