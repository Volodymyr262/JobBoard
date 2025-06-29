import pytest
from jobs.models import SavedJob


@pytest.mark.django_db
def test_user_can_save_job(auth_client_applicant, job, applicant):
    response = auth_client_applicant.post("/api/saved-jobs/", {"job": job.id})
    assert response.status_code == 201
    assert response.data["job"] == job.id
    assert SavedJob.objects.filter(user__id=applicant.id, job=job).exists()


@pytest.mark.django_db
def test_user_can_unsave_job(auth_client_applicant, applicant, job):
    SavedJob.objects.create(user=applicant, job=job)
    response = auth_client_applicant.delete(f"/api/saved-jobs/{job.id}/unsave/")
    assert response.status_code == 204
    assert not SavedJob.objects.filter(user=applicant, job=job).exists()


@pytest.mark.django_db
def test_unauthenticated_user_cannot_save(api_client, job):
    response = api_client.post("/api/saved-jobs/", {"job_id": job.id})
    assert response.status_code == 401


@pytest.mark.django_db
def test_unauthenticated_user_cannot_unsave(api_client, job):
    response = api_client.delete(f"/api/saved-jobs/{job.id}/unsave/")
    assert response.status_code == 401


@pytest.mark.django_db
def test_cannot_save_nonexistent_job(auth_client_applicant):
    invalid_id = 99999
    response = auth_client_applicant.post("/api/saved-jobs/", {"job": invalid_id})
    print(response.data)
    assert response.status_code == 400
    assert "object does not exist" in str(response.data)


@pytest.mark.django_db
def test_cannot_save_same_job_twice(auth_client_applicant, applicant, job):
    SavedJob.objects.create(user=applicant, job=job)
    response = auth_client_applicant.post("/api/saved-jobs/", {"job_id": job.id})
    assert response.status_code in (400, 409) # depends on your validation
    assert SavedJob.objects.filter(user=applicant, job=job).count() == 1


@pytest.mark.django_db
def test_unsave_job_not_previously_saved(auth_client_applicant, job):
    response = auth_client_applicant.delete(f"/api/saved-jobs/{job.id}/unsave/")
    assert response.status_code == 400 or response.status_code == 404
    assert "Not saved" in str(response.data["detail"])