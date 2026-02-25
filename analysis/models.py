from django.conf import settings
from django.db import models


class Analysis(models.Model):
    # user_id: 어떤 유저의 분석 데이터인지 (FK)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="analyses", verbose_name="분석 대상 유저")

    # period_type: 분석 기간 단위 (weekly, monthly)
    period_type = models.CharField(max_length=20, verbose_name="분석 기간 단위")

    # start_date: 분석 시작일
    start_date = models.DateField(verbose_name="분석 시작일")

    # end_date: 분석 종료일
    end_date = models.DateField(verbose_name="분석 종료일")

    # description: 분석 결과 설명
    description = models.TextField(verbose_name="분석 결과 설명")

    # result_image_url: 그래프 이미지 파일
    # 저장 경로 예시: media/analysis/charts/2026/02/파일명
    result_image = models.ImageField(upload_to="analysis/charts/%Y/%m/", null=True, blank=True, verbose_name="분석 결과 이미지")

    # created_at: 분석 리포트 생성 시간
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성 시간")

    # updated_at: 분석 리포트 수정 시간
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정 시간")

    def __str__(self):
        return f"[{self.user.nickname}] {self.target_type} 리포트 ({self.start_date} ~ {self.end_date})"

    class Meta:
        db_table = "analysis"
        verbose_name = "분석 데이터"
        verbose_name_plural = "분석 데이터 목록"
