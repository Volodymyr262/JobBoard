from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        RECRUITER = 'recruiter', 'Recruiter'
        APPLICANT = 'applicant', 'Applicant'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.APPLICANT)

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_recruiter(self):
        return self.role == self.Role.RECRUITER

    def is_applicant(self):
        return self.role == self.Role.APPLICANT
