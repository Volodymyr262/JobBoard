from http.client import responses

import pytest
from users.models import User
from rest_framework.test import APIClient

@pytest.fixture
def create_user(db):
    return User.objects.create_user(username="jwtuser", password="jwtpass123", role="applicant")

@pytest.fixture
def api_client():
    return APIClient()

def test_login_user(api_client, create_user):
    response = api_client.post('/api/token/', {
        'username': create_user.username,
        'password': 'jwtpass123',
    }, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_login_wrong_password(api_client, create_user):
    response = api_client.post('/api/token/', {
        'username': create_user.username,
        'password': 'wrondg_pass',
    }, format='json')

    assert response.status_code == 401


def test_access_protected_route(api_client, create_user):
    # Step 1: Log in
    response = api_client.post('/api/token/', {
        'username': create_user.username,
        'password': 'jwtpass123',
    }, format='json')

    access_token = response.data['access']

    # Step 2: Set credentials with token
    api_client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    # Step 3: Access a protected route
    protected_response = api_client.get('/api/applications/')

    # Step 4: Assert 200 OK
    assert protected_response.status_code == 200