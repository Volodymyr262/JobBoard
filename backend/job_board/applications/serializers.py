from rest_framework import serializers
from .models import Application
from jobs.serializers import JobSerializer
from users.models import User

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ApplicationSerializer(serializers.ModelSerializer):
    job = JobSerializer(read_only=True)
    applicant = ApplicantSerializer(read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'job', 'applicant', 'resume', 'cover_letter',
            'status', 'applied_at'
        ]
        read_only_fields = ['applicant', 'status', 'applied_at']
