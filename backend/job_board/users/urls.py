from django.urls import path
from users.views import RequestPasswordResetView, ConfirmPasswordResetView

urlpatterns = [
    path("password-reset/", RequestPasswordResetView.as_view(), name="password-reset"),
    path("password-reset/confirm/", ConfirmPasswordResetView.as_view(), name="password-reset-confirm"),
]