import pytest
from applications.models import Application, AutoResponse
from notifications.tasks import send_application_status_email
from unittest.mock import patch


@pytest.mark.django_db
@patch("notifications.tasks.send_application_status_email.delay")
def test_email_sent_on_apply_with_autoresponse(mock_delay, auth_client_applicant, applicant, job):
    AutoResponse.objects.create(
        job=job,
        event="on_apply",
        subject="Thanks for Applying!",
        body="We'll review your application shortly."
    )

    response = auth_client_applicant.post("/api/applications/", data={"job": job.id})
    assert response.status_code == 201

    mock_delay.assert_called_once()
    _, kwargs = mock_delay.call_args

    assert kwargs["to_email"] == applicant.email
    assert "review your application" in kwargs["message"]
    assert "Thanks for Applying" in kwargs["subject"]


@pytest.mark.django_db
@patch("notifications.tasks.send_application_status_email.delay")
def test_email_sent_on_apply_with_default_message(mock_delay, auth_client_applicant, applicant, job):
    response = auth_client_applicant.post("/api/applications/", data={"job": job.id})
    assert response.status_code == 201

    mock_delay.assert_called_once()
    _, kwargs = mock_delay.call_args

    assert kwargs["to_email"] == applicant.email
    assert job.title in kwargs["subject"]
    assert "Thanks for applying" in kwargs["message"]


@pytest.mark.django_db
@patch("notifications.tasks.send_application_status_email.delay")
def test_email_sent_on_status_change_with_autoresponse(mock_delay, auth_client_applicant, auth_client_recruiter, recruiter, applicant, job):
    app = Application.objects.create(applicant=applicant, job=job)

    AutoResponse.objects.create(
        job=job,
        event="on_status_change",
        subject="You got in!",
        body="Welcome aboard!"
    )

    response = auth_client_recruiter.post(
        f"/api/applications/{app.id}/update_status/",
        data={"status": "viewed"},
        content_type="application/json"
    )
    assert response.status_code == 200

    mock_delay.assert_called_once()
    _, kwargs = mock_delay.call_args

    assert kwargs["to_email"] == applicant.email
    assert "Welcome aboard!" in kwargs["message"]
    assert "You got in!" in kwargs["subject"]


@pytest.mark.django_db
@patch("notifications.tasks.send_application_status_email.delay")
def test_email_sent_on_status_change_with_default_message(mock_delay, auth_client_applicant, auth_client_recruiter, recruiter, applicant, job):
    app = Application.objects.create(applicant=applicant, job=job)

    response = auth_client_recruiter.post(
        f"/api/applications/{app.id}/update_status/",
        data={"status": "rejected"},
        content_type="application/json"
    )
    assert response.status_code == 200

    mock_delay.assert_called_once()
    _, kwargs = mock_delay.call_args

    assert kwargs["to_email"] == applicant.email
    assert "rejected" in kwargs["message"].lower()
    assert "status" in kwargs["subject"].lower()
