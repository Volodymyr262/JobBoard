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

def test_applicant_cannot_create_job(auth_client_applicant, location):
    response = auth_client_applicant.post("/api/jobs/", {
        "title": "Fake Job",
        "description": "They shouldn't be able to post this",
        "location": {
            "city": location.city,
            "country": location.country
        },
        "salary": 1234,
        "job_type": "remote",
        "experience_level": "junior"
    }, format="json")
    assert response.status_code == 403


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


def test_job_creation_missing_required_fields(auth_client_recruiter):
    response = auth_client_recruiter.post("/api/jobs/", {
        "title": "",
        "description": "",
    }, format="json")

    assert response.status_code == 400
    assert "title" in response.data or "description" in response.data

def test_unapproved_jobs_hidden(auth_client_applicant, recruiter, location):
    Job.objects.create(
        title="Secret Job",
        company=recruiter.company_profile,
        description="Shh",
        location=location,
        salary=8000,
        job_type="remote",
        experience_level="senior",
        status="pending"  # Not approved!
    )

    response = auth_client_applicant.get("/api/jobs/")
    assert response.status_code == 200
    assert all(job["status"] == "approved" for job in response.data)