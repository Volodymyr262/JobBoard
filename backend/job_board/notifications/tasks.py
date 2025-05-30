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

@shared_task
def test_real_email():
    print("📬 Sending real test email...")
    send_mail(
        subject="✅ Real Email Test from Celery",
        message="If you receive this, your email + Celery setup works!",
        from_email="volodiahedz26@gmail.com",
        recipient_list=["nemiyakk@gmail.com"],
        fail_silently=False,
    )
    print("📨 Email should be sent now.")