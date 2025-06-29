import pytest
from rest_framework.test import APIClient
from django.core import mail
from users.models import User


def test_login_user(api_client, recruiter):
    response = api_client.post('/api/token/', {
        'username': recruiter.username,
        'password': 'pass123',
    }, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_access_protected_route(api_client, recruiter):
    # Step 1: Log in
    response = api_client.post('/api/token/', {
        'username': recruiter.username,
        'password': 'pass123',
    }, format='json')

    access_token = response.data['access']

    # Step 2: Set credentials with token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    # Step 3: Access a protected route
    protected_response = api_client.get('/api/applications/')

    # Step 4: Assert 200 OK
    assert protected_response.status_code == 200


@pytest.mark.django_db
def test_register_user(api_client):
    response = api_client.post("/api/register/", {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepass123",
        "role": "applicant"
    })

    assert response.status_code == 201
    assert User.objects.filter(email="newuser@example.com").exists()
    assert len(mail.outbox) == 1
    assert "verify your jobboard account" in mail.outbox[0].subject.lower()


@pytest.mark.django_db
def test_login_success(api_client):
    user = User.objects.create_user(
        username="emailuser",
        email="emailuser@example.com",
        password="pass123"
    )

    response = api_client.post("/api/login/", {
        "email": "emailuser@example.com",
        "password": "pass123"
    })

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.django_db
def test_login_invalid_password(api_client):
    user = User.objects.create_user(
        username="wrongpass",
        email="wrongpass@example.com",
        password="correctpass"
    )

    response = api_client.post("/api/login/", {
        "email": "wrongpass@example.com",
        "password": "wrongpass123"
    })

    assert response.status_code == 401
    assert "error" in response.data