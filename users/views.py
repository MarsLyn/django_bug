from typing import Any
from django.contrib.auth.forms import AuthenticationForm
from django.forms.models import BaseModelForm
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.views import View
from django.views.generic import CreateView
from django.views.generic.edit import FormMixin
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import authenticate, get_user_model, password_validation
from django_redis import get_redis_connection


from datetime import datetime, timedelta
from uuid import uuid4

from .forms import RegisterForm, LoginForm, ImageCodeLoginForm, SendSmscodeForm
from .models import NewUser
from .script import ImageCode

from goods.models import Goods
from strategy.models import Strategy

    
class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('user:login_smscod')

    def get(self, request: HttpRequest, *args: str, **kwargs: Any):
        if request.user.is_authenticated:
            return redirect('projects:list')
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any):
        self.object = None
        form = self.get_form()
        if form.is_valid():
            print(form.cleaned_data)
            data = form.cleaned_data
            obj = NewUser(**data)
            obj.set_password(data.get('password'))
            obj.save()
            strategy_obj = Strategy.objects.filter(title='个人免费版').first()
            Goods.objects.create(
                space=uuid4(),
                status=1,
                by_user=obj,
                strategy=strategy_obj,
                amount=0,
                start_date=datetime.now(),
                num=0
            )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
        
    def form_valid(self, form: BaseModelForm):
        return redirect(reverse('user:login_smscod'))
    
class NewLoginView(LoginView):

    template_name = 'users/login.html'
    form_class = LoginForm
    next_page = reverse_lazy('projects:list')

    def get(self, request: HttpRequest, *args: str, **kwargs: Any):
        if request.user.is_authenticated:
            return redirect('projects:list')
        return super().get(request, *args, **kwargs)

class ImageCodeLoginView(LoginView):

    template_name = 'users/login_image_code.html'
    form_class = ImageCodeLoginForm
    next_page = reverse_lazy('projects:list')

    def get(self, request: HttpRequest, *args: str, **kwargs: Any):
        if request.user.is_authenticated:
            return redirect('projects:list')
        return super().get(request, *args, **kwargs)

class NewLogoutView(LogoutView):

    next_page = reverse_lazy('user:login_smscod')

class SendSmsView(FormMixin, View):

    form_class = SendSmscodeForm

    def form_valid(self, form: Any):
        return JsonResponse({'status': True, 'message': '发送成功'})
    
    def form_invalid(self, form):
        # print(dir(form))
        context = form.get_context()
        # print(context['errors'])
        return JsonResponse({'status': False, 'message': context['errors']})

    def post(self, request, *args, **kwargs):
        print(request.POST)
        if not request.user.is_authenticated:
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        
def get_img_code(request):

    if not request.user.is_authenticated:
        import base64
        from io import BytesIO

        img_code = ImageCode()
        img = img_code.get_image()
        code = img_code.get_code()

        conn = get_redis_connection()
        conn.set(code, code, 60)

        stream = BytesIO()
        img.save(stream, 'png')
        base64_data = base64.b64encode(stream.getvalue())

        return HttpResponse(base64_data)

