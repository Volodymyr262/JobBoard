from django.core.mail import send_mail
from django.conf import settings


def send_status_update_email(to_email, job_title, new_status):
    subject = f"Update on your application for {job_title}"
    message = f"Hello,\n\nYour application for '{job_title}' has been updated to: {new_status}.\n\nThank you for using our Job Board!"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,  # You need to set this in your settings.py!
        [to_email],
        fail_silently=False,  # Will raise an error if sending fails (good for debugging now)
    )


def send_application_received_email(to_email, job_title):
    subject = f"Application Received for {job_title}"
    message = f"Hi,\n\nThank you for applying to '{job_title}'. Our recruiters will review your application shortly.\n\nGood luck!"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )


def send_rejection_email(to_email, job_title):
    subject = f"Application Update for {job_title}"
    message = f"Hello,\n\nWe appreciate your interest in '{job_title}', but after careful review, we have decided to proceed with other candidates.\n\nThank you for your time and effort!"

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )
