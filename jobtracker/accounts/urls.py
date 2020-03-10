from . import views
from django.urls import path
from django.contrib.auth import views as auth

urlpatterns = [
    path('register/', views.AccountRegisterView.as_view(), name='register'),
    path('login/', auth.LoginView.as_view(), name='login'),
    path('logout/', auth.LogoutView.as_view(), name='logout'),
    path('password-change/', auth.PasswordChangeView.as_view(), name='password_change'),
    path('password-change/done', auth.PasswordChangeDoneView.as_view(),
        name='password_change_done'),
]
