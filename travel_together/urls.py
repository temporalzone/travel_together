from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from user import views
from django.contrib.auth import views as auth_views

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return redirect('register')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('create_group/', views.create_group, name='create_group'),
    path('group/<int:pk>/', views.group_detail, name='group_detail'),
    path('group/<int:pk>/request_join/', views.request_join, name='request_join'),
    path('group/<int:pk>/chat/', views.group_chat, name='group_chat'),
    path('group/<int:pk>/manage_requests/', views.manage_requests, name='manage_requests'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('verify_email/', views.verify_email, name='verify_email'),
]