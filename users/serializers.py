from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    """일반적인 유저 정보 조회 및 수정용"""
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'nickname', 'name', 'phone_number', 'grade', 'status', 'created_at']
        read_only_fields = ['id', 'email', 'grade', 'status', 'created_at']

class UserRegisterSerializer(serializers.ModelSerializer):
    """회원가입 전용 (비밀번호 처리 포함)"""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'nickname', 'name', 'phone_number', 'password']

    def create(self, validated_data):
        # UserManager의 create_user를 호출하여 비밀번호를 해싱 저장
        return CustomUser.objects.create_user(**validated_data)