from datetime import timedelta

from django.core.files.storage import default_storage
from django.test import TestCase
from django.utils import timezone

from users.models import CustomUser

from .analyzers import TransactionAnalyzer

# from transactions.models import Transaction  # 거래 모델 경로에 맞춰 수정
from .models import Analysis


class AnalyzerTest(TestCase):
    def setUp(self):
        """테스트 시작 전 필요한 데이터 설정"""
        self.user = CustomUser.objects.create_user(email="test@example.com", nickname="테스트유저", password="password123", name="test", phone_number="01011111111")

        # try:
        #     self.user = CustomUser.objects.get(id=1)
        # except CustomUser.DoesNotExist:
        #     # 테스트 DB에는 데이터가 없을 수 있으므로 대비책을 세워둡니다.
        #     self.user = CustomUser.objects.create_user(email="test@example.com", nickname="테스트유저", password="password123", name="test", phone_number="01011111111")

        self.start_date = timezone.now() - timedelta(days=1)
        self.start_date = timezone.now().date() - timedelta(days=7)
        self.end_date = timezone.now().date()

        # 테스트용 거래 데이터 생성 (Analyzer 내부의 fetch_and_process_data에서 사용됨)
        # 실제 Transaction 모델이 있다면 여기서 객체를 생성하세요.
        # Transaction.objects.create(user=self.user, amount=10000, type='EXPENSE', date=self.start_date)

    def test_analyzer_creates_analysis_and_image(self):
        """분석기가 Analysis 객체와 이미지 파일을 실제로 생성하는지 테스트"""

        # 1. 분석기 초기화
        analyzer = TransactionAnalyzer(user=self.user, target_type="EXPENSE", period_type="Weekly", start_date=self.start_date, end_date=self.end_date)

        # 2. 분석 실행 (save_analysis 호출)
        analysis_instance = analyzer.save_analysis()

        # 3. 검증 (Assertions)
        # 3-1. Analysis 객체가 None이 아닌지 확인
        self.assertIsNotNone(analysis_instance)

        # 테스트 도중에는 DB에 데이터가 있으므로 개수가 1이 나옵니다.
        print(f"현재 DB에 저장된 분석 개수: {Analysis.objects.count()}")

        # 3-2. DB에 실제로 저장되었는지 확인
        self.assertEqual(Analysis.objects.count(), 1)

        # 3-3. 이미지 파일이 필드에 할당되었고 실제로 존재하는지 확인
        self.assertTrue(bool(analysis_instance.result_image))
        self.assertTrue(default_storage.exists(analysis_instance.result_image.name))

        # 3-4. 필드 데이터가 정확한지 확인
        self.assertEqual(analysis_instance.user, self.user)
        self.assertEqual(analysis_instance.target_type, "EXPENSE")

    def tearDown(self):
        """테스트 완료 후 생성된 테스트 이미지 파일 삭제 (저장소 정리)"""
        # analyses = Analysis.objects.all()
        # for analysis in analyses:
        #     if analysis.result_image:
        #         analysis.result_image.delete(save=False)
        pass
