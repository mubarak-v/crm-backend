# users/urls.py
from django.urls import path
from .views import (
    RegisterView, 
    LoginView,
    GenerateVerificationCodeView,
    VerifyCodeView,
    UserProfileView,
    UserListView
)

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # Verification and password reset endpoints
    path('generate-verification-code/', GenerateVerificationCodeView.as_view(), name='generate-verification-code'),
    path('verify-code/', VerifyCodeView.as_view(), name='verify-code'),
    # User profile endpoint
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    # All users endpoint
    path('users/', UserListView.as_view(), name='user-list'),
]
     

