import pytest
from jobs.models import Job, Location, CompanyProfile
from django.urls import reverse
import time
from jobs.documents import JobDocument


@pytest.mark.django_db
def test_fuzzy_search_matches_typos(auth_client_applicant, recruiter, location):
    job = Job.objects.create(
        title="Python Developer",
        company=recruiter.company_profile,
        description="Backend role with Django",
        location=location,
        salary=9000,
        job_type="remote",
        experience_level="mid",
        status="approved"
    )
    JobDocument().update(job, refresh=True, action='index')

    # Give time for ES to index (or use refresh=True in real app)
    time.sleep(1)

    response = auth_client_applicant.get("/api/search/?q=pythn dev")
    assert response.status_code == 200
    results = response.json()["results"]

    assert any("Python Developer" in r["title"] for r in results)


@pytest.mark.django_db
def test_search_suggestions_work(auth_client_applicant, recruiter, location):
    job = Job.objects.create(
        title="JavaScript Engineer",
        company=recruiter.company_profile,
        description="Frontend wizard wanted",
        location=location,
        salary=8000,
        job_type="onsite",
        experience_level="senior",
        status="approved"
    )
    JobDocument().update(job, refresh=True, action='index')
    time.sleep(1)

    response = auth_client_applicant.get("/api/search/?q=javacript")
    assert response.status_code == 200
    suggestions = response.json()["suggestions"]

    assert any("javascript" in s.lower() for s in suggestions)


@pytest.mark.django_db
def test_autocomplete_prefix_matches(auth_client_applicant, recruiter, location):
    job = Job.objects.create(
        title="DevOps Engineer",
        company=recruiter.company_profile,
        description="AWS + Docker + Python",
        location=location,
        salary=9500,
        job_type="hybrid",
        experience_level="senior",
        status="approved"
    )
    JobDocument().update(job, refresh=True, action='index')
    time.sleep(1)

    response = auth_client_applicant.get("/api/search/?q=devop")
    assert response.status_code == 200
    data = response.json()

    assert any("DevOps Engineer" in r["title"] for r in data["results"])
    assert any("devops" in s.lower() for s in data["suggestions"])


@pytest.mark.django_db
def test_no_results_no_suggestions(auth_client_applicant):
    response = auth_client_applicant.get("/api/search/?q=asdkfjweior")  # gibberish
    assert response.status_code == 200
    data = response.json()

    assert data["results"] == []
    assert data["suggestions"] == []
