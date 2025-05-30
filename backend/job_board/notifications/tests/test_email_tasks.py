import pytest
from django.core import mail
from notifications.tasks import send_application_status_email


@pytest.mark.django_db
def test_send_application_status_email():
    # Run the task synchronously (like Celery worker does)
    send_application_status_email(
        to_email="nemiyakk@gmail.com",
        subject="Test Email Subject",
        message="This is a test message."
    )

    # Assert email was created
    assert len(mail.outbox) == 1
    email = mail.outbox[0]

    assert email.subject == "Test Email Subject"
    assert "This is a test message." in email.body
    assert email.to == ["nemiyakk@gmail.com"]
