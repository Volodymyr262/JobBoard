import pytest
from django.core import mail
from django.core.mail import BadHeaderError
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


def test_invalid_email_raises_error():
    with pytest.raises(BadHeaderError):
        # Directly call the task's core logic
        send_application_status_email.run(
            to_email="\ninvalid@email.com",
            subject="Bad Header",
            message="Header injection test"
        )


@pytest.mark.django_db
def test_send_email_multiple_recipients():
    recipients = ["user1@example.com", "user2@example.com"]

    for recipient in recipients:
        send_application_status_email(
            to_email=recipient,
            subject="Test Group Email",
            message="Hello group!"
        )

    assert len(mail.outbox) == len(recipients)
    for i, recipient in enumerate(recipients):
        assert mail.outbox[i].to == [recipient]
        assert "Hello group!" in mail.outbox[i].body

@pytest.mark.django_db
def test_send_email_with_empty_subject_and_body():
    send_application_status_email.run(
        to_email="test@example.com",
        subject="",
        message=""
    )

    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.subject == ""
    assert email.body == ""


def test_send_email_with_long_subject_and_body():
    long_subject = "A" * 255
    long_body = "B" * 5000

    send_application_status_email.run(
        to_email="test@example.com",
        subject=long_subject,
        message=long_body
    )

    email = mail.outbox[0]
    assert email.subject == long_subject
    assert email.body == long_body