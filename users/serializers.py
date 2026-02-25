from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import CustomUser


# ModelSerializer: 기본적인 CRUD가 구현된 반자동 레시피
# Serializer: 내가 직접 구현하는 수동 레시피(주 DB에서 다루지않는 데이터를 다룰때)
class UserSerializer(serializers.ModelSerializer):
    """일반적인 유저 정보 조회 및 수정용"""

    class Meta:
        model = CustomUser
        fields = ["id", "email", "nickname", "name", "phone_number", "grade", "status", "created_at"]
        read_only_fields = ["id", "email", "grade", "status", "created_at"]


class UserRegisterSerializer(serializers.ModelSerializer):
    """회원가입 전용 (비밀번호 처리)"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["email", "nickname", "name", "phone_number", "password"]

    def create(self, validated_data):
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """유저 로그인"""

    email = serializers.EmailField(help_text="사용자 이메일")
    password = serializers.CharField(write_only=True, style={"input_type": "password"}, help_text="사용자 비밀번호")

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError("이메일 또는 비밀번호가 잘못되었습니다.")

            # 삭제 대기 중이거나 삭제된 유저는 로그인 불가 처리
            if user.status == "DELETED":
                raise serializers.ValidationError("로그인할 수 없는 계정 상태입니다.")
        else:
            raise serializers.ValidationError("이메일과 비밀번호를 모두 입력해주세요.")

        data["user"] = user
        return data
