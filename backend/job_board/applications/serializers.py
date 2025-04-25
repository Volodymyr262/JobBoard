from rest_framework import serializers
from .models import Application
from jobs.models import Job
from jobs.serializers import JobSerializer
from users.models import User

class ApplicantSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class ApplicationSerializer(serializers.ModelSerializer):
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.all())
    applicant = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Application
        fields = [
            'id', 'job', 'applicant', 'resume', 'cover_letter',
            'status', 'applied_at'
        ]
        read_only_fields = ['applicant', 'status', 'applied_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['status_choices'] = [
            {"value": choice[0], "label": choice[1]}
            for choice in Application.ApplicationStatus.choices
        ]
        return data