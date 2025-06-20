import pytest
from django.core import mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from users.models import User

@pytest.mark.django_db
def test_verification_email_sent_on_register(client):
    response = client.post("/api/register/", {
        "username": "newuser",
        "email": "verifyme@example.com",
        "password": "securepass123"
    })

    assert response.status_code == 201
    assert len(mail.outbox) == 1

    email = mail.outbox[0]
    assert "verify" in email.subject.lower()
    assert "verify" in email.body.lower()
    assert "verifyme@example.com" in email.to


@pytest.mark.django_db
def test_email_verified_successfully(client):
    user = User.objects.create_user(
        username="verifiable",
        email="verify@example.com",
        password="pass123",
        is_active=True
    )

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = client.get(f"/api/verify-email/?uid={uid}&token={token}")
    assert response.status_code == 200

    user.refresh_from_db()
    assert user.is_email_verified is True


@pytest.mark.django_db
def test_invalid_verification_token(client):
    user = User.objects.create_user(
        username="broken",
        email="invalid@example.com",
        password="pass123"
    )

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    invalid_token = "totally-invalid-token"

    response = client.get(f"/api/verify-email/?uid={uid}&token={invalid_token}")
    assert response.status_code == 400

    user.refresh_from_db()
    assert not getattr(user, "is_email_verified", False)


@pytest.mark.django_db
def test_reverify_does_not_crash(client):
    user = User.objects.create_user(
        username="alreadyverified",
        email="yup@example.com",
        password="pass123",
        is_active=True
    )
    user.is_email_verified = True
    user.save()

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    response = client.get(f"/api/verify-email/?uid={uid}&token={token}")
    assert response.status_code in (200, 400)
