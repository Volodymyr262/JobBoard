import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

def test_login_user(api_client, recruiter):
    response = api_client.post('/api/token/', {
        'username': recruiter.username,
        'password': 'pass123',
    }, format='json')

    assert response.status_code == 200
    assert 'access' in response.data
    assert 'refresh' in response.data


def test_login_wrong_password(api_client, recruiter):
    response = api_client.post('/api/token/', {
        'username': recruiter.username,
        'password': 'wrondg_pass',
    }, format='json')

    assert response.status_code == 401


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