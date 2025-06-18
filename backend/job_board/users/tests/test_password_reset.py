import pytest
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_password_reset_email_sent(client):
    user = User.objects.create_user(username="tester", email="test@example.com", password="initial123")

    response = client.post("/api/password-reset/", {"email": "test@example.com"})
    assert response.status_code == 200
    assert len(mail.outbox) == 1
    assert "Reset your password" in mail.outbox[0].body


@pytest.mark.django_db
def test_password_reset_confirm_success(client):
    user = User.objects.create_user(username="resetme", email="reset@example.com", password="oldpass123")
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = client.post("/api/password-reset/confirm/", {
        "uid": uid,
        "token": token,
        "new_password": "newpass456"
    })

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("newpass456")


@pytest.mark.django_db
def test_password_reset_confirm_invalid_token(client):
    user = User.objects.create_user(username="resetme", email="reset@example.com", password="oldpass123")
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = "invalid-token"

    response = client.post("/api/password-reset/confirm/", {
        "uid": uid,
        "token": token,
        "new_password": "newpass456"
    })

    assert response.status_code == 400
