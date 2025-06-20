from django.urls import path
from users.views import RequestPasswordResetView, ConfirmPasswordResetView, VerifyEmailView, RegisterView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path("password-reset/", RequestPasswordResetView.as_view(), name="password-reset"),
    path("password-reset/confirm/", ConfirmPasswordResetView.as_view(), name="password-reset-confirm"),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email')
]