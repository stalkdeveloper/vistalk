from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('',                            views.HomeView.as_view(),           name='home'),
    path('register/',                   views.PlatformRegisterView.as_view(), name='register'),
    path('login/',                      views.PlatformLoginView.as_view(),  name='login'),
    path('logout/',                     views.LogoutView.as_view(),         name='logout'),
    path('forgot-password/',            views.ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/<str:token>/', views.ResetPasswordView.as_view(),  name='reset_password'),
    path('admin/login/',                views.SystemLoginView.as_view(),    name='system_login'),
]