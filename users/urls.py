from django.urls import path
from .views import (
    RegisterView, 
    NewLoginView, 
    ImageCodeLoginView,
    NewLogoutView, 
    SendSmsView,
    get_img_code
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', NewLoginView.as_view(), name='login_smscod'),
    path('login/img/', ImageCodeLoginView.as_view(), name='login_img'),
    path('logout/', NewLogoutView.as_view(), name='logout'),
    path('sendsms/', SendSmsView.as_view(), name='sendsms'),
    path('imgcode/', get_img_code, name='imgcode'),
]

app_name = 'user'