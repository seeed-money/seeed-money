# analysis/serializers.py
from rest_framework import serializers

from .models import Analysis


class AnalysisSerializer(serializers.ModelSerializer):
    # 환경에 맞는 URL가져옴
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Analysis
        fields = ["id", "period_type", "description", "result_image", "image_url", "created_at"]

    def get_image_url(self, obj):
        if not obj.result_image:
            print("값이 없다")
            return None

        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(obj.result_image.url)

        return obj.result_image.url
