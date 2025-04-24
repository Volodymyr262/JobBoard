from rest_framework import viewsets, permissions
from .models import Application
from .serializers import ApplicationSerializer
from api.permissions import IsApplicant, IsRecruiter

class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    queryset = Application.objects.all()

    def get_permissions(self):
        if self.action in ['create']:
            return [IsApplicant()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        if user.is_applicant():
            return Application.objects.filter(applicant=user)
        elif user.is_recruiter():
            return Application.objects.filter(job__company__owner=user)
        return Application.objects.none()

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)
