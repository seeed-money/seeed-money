from django.urls import include, path
from rest_framework.routers import DefaultRouter

# 얘가 {id}경로 자동으로 만들어줌
from .views import AccountViewSet

router = DefaultRouter()
router.register(r"", AccountViewSet, basename="account")

urlpatterns = [
    path("", include(router.urls)),
]
