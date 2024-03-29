from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from datetime import datetime, timedelta


class CustomAccountManager(BaseUserManager):

    def create_superuser(self, email, user_name, password, **other_fields):

        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError(
                '管理员必须设置 is_staff=True'
            )
        if other_fields.get('is_superuser') is not True:
            raise ValueError(
                '管理员必须设置 is_superuser=True'
            )
        
        return self.create_user(email, user_name, password, **other_fields)
    
    def create_user(self, email, user_name, password, **other_fields):

        if not email:
            raise ValueError(_('必须提供邮箱'))

        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name, **other_fields)
        user.set_password(password)
        user.save()
        return user
    

class NewUser(AbstractBaseUser, PermissionsMixin):
    
    email = models.EmailField(_('邮箱'), unique=True)
    user_name = models.CharField(_('用户名'), max_length=150, unique=True)
    start_date = models.DateTimeField(_('创建时间'), auto_now_add=True)
    about = models.TextField(_('about'), max_length=500, blank=True)
    is_staff = models.BooleanField(_('是否是工作人员'), default=False)
    is_active = models.BooleanField(_('是否激活'), default=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['user_name']

    def __str__(self):
        return self.user_name
