from django.db import models
from users.models import User
from jobs.models import Job

class Application(models.Model):
    class ApplicationStatus(models.TextChoices):
        SENT = 'sent', 'Sent'
        VIEWED = 'viewed', 'Viewed'
        SHORTLISTED = 'shortlisted', 'Shortlisted'
        REJECTED = 'rejected', 'Rejected'

    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.SENT)
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant.username} applied to {self.job.title}"
