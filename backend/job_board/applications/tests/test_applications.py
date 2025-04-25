from applications.models import Application

APPLICATION_URL = '/api/applications/'

def test_applicant_can_apply_to_job(auth_client_applicant, job):
    response = auth_client_applicant.post(APPLICATION_URL, {
        "job": job.id,
        "cover_letter": "I am interested!"
    })
    assert response.status_code == 201
    assert Application.objects.filter(job=job).exists()

def test_applicant_sees_own_applications(auth_client_applicant, job, applicant):
    Application.objects.create(applicant=applicant, job=job, cover_letter="Yooo")
    response = auth_client_applicant.get(APPLICATION_URL)
    assert response.status_code == 200
    assert len(response.data) >= 1

def test_recruiter_can_change_status(auth_client_recruiter, applicant, job):
    # Step 1: Create application
    app = Application.objects.create(applicant=applicant, job=job, cover_letter="Please hire me.")

    # Step 2: Recruiter updates status to 'shortlisted'
    response = auth_client_recruiter.post(f"{APPLICATION_URL}{app.id}/update_status/", {
        "status": "shortlisted"
    }, format="json")

    # Step 3: Assert status updated
    assert response.status_code == 200
    app.refresh_from_db()
    assert app.status == "shortlisted"
    assert response.data['status'] == "shortlisted"


def test_recruiter_cannot_use_invalid_status(auth_client_recruiter, applicant, job):
    app = Application.objects.create(applicant=applicant, job=job, cover_letter="Try again?")

    response = auth_client_recruiter.post(f'{APPLICATION_URL}{app.id}/update_status/',{
        "status": "undefined"
    }, format='json')

    assert response.status_code == 400
    assert "error" in response.data



def test_applicant_cannot_change_status(auth_client_applicant,applicant, recruiter, job):
    app = Application.objects.create(applicant=applicant, job=job, cover_letter="bib")

    response = auth_client_applicant.post(f"{APPLICATION_URL}{app.id}/update_status/", {
        "status": "rejected"
    }, format="json")

    assert response.status_code == 403