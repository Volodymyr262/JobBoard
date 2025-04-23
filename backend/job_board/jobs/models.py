from django.db import models
from users.models import User

class Location(models.Model):
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city}, {self.country}"

class CompanyProfile(models.Model):
    name = models.CharField(max_length=255, unique=True)
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    description = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    class JobStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    class JobType(models.TextChoices):
        ONSITE = 'onsite', 'On-site'
        REMOTE = 'remote', 'Remote'
        HYBRID = 'hybrid', 'Hybrid'

    class ExperienceLevel(models.TextChoices):
        JUNIOR = 'junior', 'Junior'
        MID = 'mid', 'Mid'
        SENIOR = 'senior', 'Senior'

    title = models.CharField(max_length=255)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='jobs')
    description = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, related_name='jobs')
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    job_type = models.CharField(max_length=10, choices=JobType.choices)
    experience_level = models.CharField(max_length=10, choices=ExperienceLevel.choices)
    status = models.CharField(max_length=10, choices=JobStatus.choices, default=JobStatus.PENDING)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} @ {self.company.name}"
