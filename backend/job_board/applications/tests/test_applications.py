import pytest
from rest_framework.test import APIClient
from users.models import User
from jobs.models import Job, Location, CompanyProfile
from applications.models import Application


def test_applicant_can_apply_to_job(auth_client_applicant, job):
    response = auth_client_applicant.post("/api/applications/", {
        "job": job.id,
        "cover_letter": "I am interested!"
    })
    assert response.status_code == 201
    assert Application.objects.filter(job=job).exists()

def test_applicant_sees_own_applications(auth_client_applicant, job, applicant):
    Application.objects.create(applicant=applicant, job=job, cover_letter="Yooo")
    response = auth_client_applicant.get("/api/applications/")
    assert response.status_code == 200
    assert len(response.data) >= 1
