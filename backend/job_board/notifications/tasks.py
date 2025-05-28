from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_application_status_email(to_email, subject, message):
    print("📨 Sending async email...")
    send_mail(
        subject,
        message,
        'noreply@jobboard.com',
        [to_email],
        fail_silently=False,
    )
    print("✅ Email sent.")
