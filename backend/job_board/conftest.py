import os
import django
import pytest
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_board.settings')
django.setup()
from rest_framework.test import APIClient
from users.models import User
from jobs.models import Location, CompanyProfile, Job
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def recruiter(db):
    user = User.objects.create_user(username="recruiter1", password="pass123", role="recruiter", is_email_verified=True)
    CompanyProfile.objects.create(name="Test Co", owner=user)
    return user

@pytest.fixture
def applicant(db):
    return User.objects.create_user(username="applicant1", password="pass123", role="applicant", is_email_verified=True)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

@pytest.fixture
def auth_client_applicant(applicant):
    client = APIClient()
    token = get_tokens_for_user(applicant)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client

@pytest.fixture
def auth_client_recruiter(recruiter):
    client = APIClient()
    token = get_tokens_for_user(recruiter)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client

@pytest.fixture
def location():
    return Location.objects.create(city="Warsaw", country="Poland")

@pytest.fixture
def job(recruiter, location):
    return Job.objects.create(
        title="Fullstack Dev",
        company=recruiter.company_profile,
        description="Build cool stuff",
        location=location,
        salary=7000,
        job_type="onsite",
        experience_level="senior",
        status="approved"
    )
