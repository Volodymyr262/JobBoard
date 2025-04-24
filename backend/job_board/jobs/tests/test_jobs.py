import pytest
from rest_framework.test import APIClient
from users.models import User
from jobs.models import Job, Location, CompanyProfile



def test_recruiter_can_create_job(auth_client_recruiter, location):
    response = auth_client_recruiter.post("/api/jobs/", {
        "title": "Backend Dev",
        "description": "Cool job",
        "location": {
            "city": location.city,
            "country": location.country
        },
        "salary": 6000,
        "job_type": "remote",
        "experience_level": "mid"
    }, format="json")
    assert response.status_code == 201
    assert response.data['title'] == "Backend Dev"

def test_applicant_can_filter_jobs(auth_client_applicant, recruiter, location):
    # Create a job manually
    job = Job.objects.create(
        title="Python Dev",
        company=recruiter.company_profile,
        description="Remote position",
        location=location,
        salary=5000,
        job_type="remote",
        experience_level="junior",
        status="approved"
    )

    response = auth_client_applicant.get("/api/jobs/?location__city=Warsaw&min_salary=3000")
    assert response.status_code == 200
    assert len(response.data) >= 1
    assert response.data[0]["title"] == "Python Dev"
