from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Func


class ApiUser(AbstractUser):
    ...


from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLES = (
        ('user', 'Обычный пользователь'),
        ('admin', 'Администратор'),
        ('publisher', 'Публикатор'),
    )

    role = models.CharField(max_length=10, choices=ROLES, default='user')
    telegram_chat_id = models.CharField(max_length=30, blank=True, null=True)
    can_publish = models.BooleanField(default=False)

    def __str__(self):
        return self.username


from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class UserManager(BaseUserManager):
    def create_user(self, login, password=None, **extra_fields):
        if not login:
            raise ValueError('The Login field must be set')
        user = self.model(login=login, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, login, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('can_write', True)
        return self.create_user(login, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=20)
    patronymic = models.CharField(max_length=20)
    is_admin = models.BooleanField(default=False)
    can_write = models.BooleanField(default=True)
    telegram = models.CharField(max_length=30, blank=True, null=True)

    login = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=128)  # Django хранит хэш пароля

    USERNAME_FIELD = 'login'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'patronymic']

    objects = UserManager()

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.patronymic}"

    class Meta:
        db_table = 'users'
