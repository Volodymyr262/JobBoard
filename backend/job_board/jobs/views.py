from rest_framework import viewsets, permissions
from .models import Job, Location, CompanyProfile
from .serializers import JobSerializer, CompanyProfileSerializer, LocationSerializer
from api.permissions import IsRecruiter, IsAdmin
from .filters import JobFilter
from django_filters.rest_framework import DjangoFilterBackend


class JobViewSet(viewsets.ModelViewSet):
    serializer_class = JobSerializer
    queryset = Job.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = JobFilter

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsRecruiter()]
        return [permissions.AllowAny()]

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_recruiter():
                return Job.objects.filter(company__owner=user)
            elif user.is_admin():
                return Job.objects.filter(status='pending')
        return Job.objects.filter(status='approved')

    def perform_create(self, serializer):
        company = self.request.user.company_profile
        serializer.save(company=company)


class CompanyProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsRecruiter]
    queryset = CompanyProfile.objects.all()

    def get_queryset(self):
        return CompanyProfile.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = [permissions.AllowAny]