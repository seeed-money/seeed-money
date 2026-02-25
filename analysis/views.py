from datetime import timedelta

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import BaseRenderer

from .analyzers import TransactionAnalyzer
from .models import Analysis
from .serializers import AnalysisSerializer


# --- 1. 분석 리스트 및 자동 생성 View ---
class AnalysisListView(ListAPIView):
    """
    유저의 분석 결과 리스트를 반환합니다.
    데이터가 없을 경우 실시간으로 분석을 수행하여 생성합니다.
    """

    serializer_class = AnalysisSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # 기간 추출 -> 기본은 month
        period = self.request.query_params.get("period", "monthly")

        # 오늘날짜로 데이터가 있는지 확인
        queryset = Analysis.objects.filter(user=user, period_type__iexact=period)

        # 데이터가 없다면 즉석에서 생성 로직 실행
        if not queryset.exists():
            self.create_on_the_fly_analysis(user, period)
            # 생성 후 다시 조회하여 반환할 쿼리셋 갱신
            queryset = Analysis.objects.filter(user=user, period_type__iexact=period)

        return queryset.order_by("-created_at")

    def create_on_the_fly_analysis(self, user, period):
        """데이터가 없을 때 TransactionAnalyzer를 사용하여 분석 수행 및 저장"""
        end_date = timezone.now().date()

        # 기간 계산 로직
        if period.lower() == "monthly":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)

        # 분석기 생성
        analyzer = TransactionAnalyzer(
            user=user,
            period_type=period.capitalize(),
            start_date=start_date,
            end_date=end_date,
        )

        # 분석 실행, 그래프 생성 및 DB 저장
        analyzer.save_analysis()


class ImageRenderer(BaseRenderer):
    media_type = "image/png"
    format = "png"
    charset = None
    render_style = "binary"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


# 이미지 렌더링
@api_view(["GET"])
@permission_classes([IsAuthenticated])
@renderer_classes([ImageRenderer])  # 만든 이미지 렌더러 적용
def analysis_image_render(request, pk):
    analysis = get_object_or_404(Analysis, pk=pk, user=request.user)

    if not analysis.result_image:
        return HttpResponse(status=404)

    # .read()는 바이너리 데이터를 직접 가져옵니다.
    image_data = analysis.result_image.read()

    # HttpResponse에 content_type을 명시하여 보냅니다.
    return HttpResponse(image_data, content_type="image/png")
