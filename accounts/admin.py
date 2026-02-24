# Register your models here.
from django.contrib import admin

from .models import Account  # Account 모델 임포트


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    # 관리자 목록 화면에서 보여줄 항목들
    list_display = ("account_name", "account_number", "balance", "bank_code", "account_type", "is_main", "user")
    # 클릭 시 상세 페이지로 이동할 필드
    list_display_links = ("account_name", "account_number")
    # 우측 필터 바 추가 (은행별, 유형별로 모아보기)
    list_filter = ("bank_code", "account_type", "is_main")
    # 검색 기능 추가
    search_fields = ("account_name", "account_number")
