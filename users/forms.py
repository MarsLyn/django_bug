from typing import Any
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, get_user_model, password_validation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.shortcuts import get_object_or_404
from django.db.models import F
from django_redis import get_redis_connection


import random
from datetime import datetime, timedelta


from .models import NewUser

UserModel = get_user_model()

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='密码', 
        required=True, 
        widget=(forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "password",}))
    )
    class Meta:
        model = NewUser
        fields = ['email', 'user_name']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': "name@example.com",
            }),
            'user_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': "name",
            }),
        }

class LoginForm(AuthenticationForm):

    username = forms.CharField(label='邮箱', required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "email", "autofocus": True}))
    password = forms.CharField(label='密码', required=True, strip=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "password", "autocomplete": "current-password"}))
    smscode = forms.CharField(label='短信验证码', required=True, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': "smscode"}))

    error_messages = {
        'invalid_login': _(
            "请输入正确的%(username)s和密码。请注意两者字段可能区分大小写。"
        ),
        "inactive": _("此帐户处于非活动状态。"),
        "smscode_length": _("验证码无效"),
        "smscode_expired": _("验证码已过期"),
    }

    def __init__(self, request=None, *args: Any, **kwargs: Any):
        super().__init__(request, *args, **kwargs)

    def clean_smscode(self):
        smscode = self.cleaned_data.get('smscode')
        email = self.cleaned_data.get('username')

        if len(smscode) < 5:
            self.get_smscode_error(error=self.error_messages['smscode_length'])

        conn = get_redis_connection()
        r_code = conn.get(email)

        if r_code:
        
            # object = get_object_or_404(SmsCode, smscode=int(smscode))

            # if object.get_code_type_display() != '登录':
            #     self.get_smscode_error(error=self.error_messages['smscode_length'])

            # if object.is_expired:
            #     self.get_smscode_error(error=self.error_messages['smscode_expired'])

            # if datetime.now() > object.expired_date:
            #     object.is_expired = True
            #     object.save()
            #     self.get_smscode_error(error=self.error_messages['smscode_expired'])

            return smscode
        else:
            self.get_smscode_error(error=self.error_messages['smscode_expired'])
    
    def get_smscode_error(self, error):
        raise ValidationError(
            error,
            code='400'
        )
    
class ImageCodeLoginForm(AuthenticationForm):

    username = forms.CharField(label='邮箱', required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "email", "autofocus": True}))
    password = forms.CharField(label='密码', required=True, strip=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "password", "autocomplete": "current-password"}))
    imgcode = forms.CharField(label='验证码', required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': "imgcode"}))

    error_messages = {
        'invalid_login': _(
            "请输入正确的%(username)s和密码。请注意两者字段可能区分大小写。"
        ),
        "inactive": _("此帐户处于非活动状态。"),
        "smscode_expired": _("验证码已过期,请重新获取"),
    }

    def __init__(self, request=None, *args: Any, **kwargs: Any):
        super().__init__(request, *args, **kwargs)
    

    def clean_imgcode(self):
        imgcode = self.cleaned_data.get('imgcode')
        conn = get_redis_connection()
        r_code = conn.get(imgcode.strip().upper())
        # print(r_code)

        if not r_code:
            self.get_imgcod_error(error=self.error_messages['smscode_expired']) 

        return imgcode

    def get_imgcod_error(self, error):
        raise ValidationError(
            error,
            code='400'
        )

class SendSmscodeForm(AuthenticationForm):

    username = forms.CharField(label='邮箱', required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': "email", "autofocus": True}))
    password = forms.CharField(label='密码', required=True, strip=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': "password", "autocomplete": "current-password"}))

    error_messages = {
        'invalid_login': _(
            "请输入正确的%(username)s和密码。请注意两者字段可能区分大小写。"
        ),
        "inactive": _("此帐户处于非活动状态。"),
    }

    def clean(self):
        super().clean()
        smscode = random.randrange(100000, 999999)
        print(smscode)
        # SmsCode.objects.create(
        #     smscode=smscode,
        #     user=self.get_user(form),
        #     expired_date=datetime.now() + timedelta(minutes=3)
        # )
        conn = get_redis_connection()
        conn.set(self.cleaned_data.get('username'), smscode, 60)