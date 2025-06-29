from rest_framework import serializers
from .models import Job, CompanyProfile, Location, SavedJob


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'city', 'country']

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = ['id', 'name', 'description', 'website', 'logo']

class JobSerializer(serializers.ModelSerializer):
    company = CompanyProfileSerializer(read_only=True)
    location = LocationSerializer()

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'description', 'location',
            'salary', 'job_type', 'experience_level', 'status', 'created_at'
        ]
        read_only_fields = ['status', 'company', 'created_at']

    def create(self, validated_data):
        # Extract nested location data and get/create it
        location_data = validated_data.pop('location')
        location, _ = Location.objects.get_or_create(**location_data)
        job = Job.objects.create(location=location, **validated_data)
        return job

    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        if location_data:
            location, _ = Location.objects.get_or_create(**location_data)
            instance.location = location

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class SavedJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = SavedJob
        fields = ['id', 'job', 'saved_at']