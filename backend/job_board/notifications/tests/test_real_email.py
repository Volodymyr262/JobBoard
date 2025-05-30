# notifications/tests/test_real_email.py

import pytest
from django.core.mail import send_mail

@pytest.mark.django_db
def test_real_email_delivery():
    sent = send_mail(
        subject="🔥 Real Email Test from Django",
        message="If you see this, your SMTP config works!",
        from_email="volodiahedz26@gmail.com",   # must match EMAIL_HOST_USER
        recipient_list=["nemiyakk@gmail.com"],  # or another test inbox
        fail_silently=False,
    )
    assert sent == 1
