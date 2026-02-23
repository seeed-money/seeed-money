from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


# 유저 데이터가 들어올때 이메일혈식, 필수필드 검증 등 pydantic의 기능을 수행한다
class CustomUserManager(BaseUserManager):
    def create_user(self, email, nickname, name, phone_number, password=None, **kwargs):
        if not email:
            raise ValueError("이메일은 필수 항목입니다.")
        if not phone_number:
            raise ValueError("핸드폰 번호는 필수 항목입니다.")

        email = self.normalize_email(email)
        user = self.model(email=email, nickname=nickname, name=name, phone_number=phone_number, **kwargs)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nickname, name, phone_number, password=None, **kwargs):
        kwargs.setdefault("is_superuser", True)
        kwargs.setdefault("is_staff", True)
        kwargs.setdefault("grade", 3)  # 관리자는 등급 3으로 설정

        return self.create_user(email, nickname, name, phone_number, password, **kwargs)


# 기존에 쓰던 유저 모델을 상속받아 일부만 추가,수정하여 사용함
class CustomUser(AbstractUser):
    username = None
    first_name = None
    last_name = None

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "활성"
        DELETING = "DELETING", "삭제 대기"
        DELETED = "DELETED", "삭제 완료"

    email = models.EmailField(unique=True, max_length=255, verbose_name="이메일")
    nickname = models.CharField(max_length=50, unique=True, verbose_name="닉네임")
    name = models.CharField(max_length=50, verbose_name="이름")
    phone_number = models.CharField(max_length=20, verbose_name="핸드폰번호")
    grade = models.IntegerField(default=1, verbose_name="회원등급 ex)1=일반회원, 2=스태프, 3=관리자")
    is_active = models.BooleanField(default=True, verbose_name="활성화 여부")
    # 상태
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="생성일")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="수정일")
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = CustomUserManager()

    # 이메일을 username으로 사용하는 설정
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nickname", "name", "phone_number"]

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]  # ORM 최적화 베스트 프랙티스
        indexes = [
            models.Index(fields=["grade"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.nickname

    # 삭제 유예기간
    def soft_delete(self):
        self.status = self.Status.DELETING
        self.deleted_at = timezone.now()
        # self.is_active = False
        self.save()

    # 삭제복구
    def undo_delete(self):
        self.status = self.Status.ACTIVE
        self.deleted_at = None
        # self.is_active = True
        self.save()

    def save(self, *args, **kwargs):
        # grade가 2(스태프) 이상이면 is_staff를 자동으로 True로 설정
        if self.grade >= 2:
            self.is_staff = True
        else:
            self.is_staff = False
        super().save(*args, **kwargs)

    @property
    def is_manager(self):
        return self.grade >= 2
