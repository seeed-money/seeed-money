from django.urls import path

from .views import AnalysisListView, analysis_image_render

urlpatterns = [
    path("", AnalysisListView.as_view(), name="analysis-list"),
    path("<int:pk>/image/", analysis_image_render, name="analysis-image-render"),  # 이미지 렌더링
]
