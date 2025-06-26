from django.urls import path, include
from users.views import RequestPasswordResetView, ConfirmPasswordResetView, VerifyEmailView, RegisterView, LoginView

urlpatterns = [
    path('login/',LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path("password-reset/", RequestPasswordResetView.as_view(), name="password-reset"),
    path("password-reset/confirm/", ConfirmPasswordResetView.as_view(), name="password-reset-confirm"),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
    path("social/", include("allauth.socialaccount.urls")),
]