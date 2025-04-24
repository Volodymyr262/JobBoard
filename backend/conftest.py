import pytest
from rest_framework.test import APIClient
from users.models import User
from jobs.models import Location, CompanyProfile, Job
from applications.models import Application

@pytest.fixture
def recruiter(db):
    user = User.objects.create_user(username="recruiter1", password="pass123", role="recruiter")
    CompanyProfile.objects.create(name="Test Co", owner=user)
    return user

@pytest.fixture
def applicant(db):
    return User.objects.create_user(username="applicant1", password="pass123", role="applicant")

@pytest.fixture
def auth_client_recruiter(recruiter):
    client = APIClient()
    client.login(username="recruiter1", password="pass123")
    return client

@pytest.fixture
def auth_client_applicant(applicant):
    client = APIClient()
    client.login(username="applicant1", password="pass123")
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
