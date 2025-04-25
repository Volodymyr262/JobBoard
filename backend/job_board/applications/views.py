from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Application
from .serializers import ApplicationSerializer
from api.permissions import IsApplicant, IsRecruiter

class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    queryset = Application.objects.all()

    def get_permissions(self):
        if self.action == "update_status":
            return [IsRecruiter()]
        elif self.action == "create":
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

    @action(detail=True, methods=['post'], permission_classes=[IsRecruiter])
    def update_status(self, request, pk=None):
        application = self.get_object()
        new_status = request.data.get('status')
        valid_statuses = [choice[0] for choice in Application.ApplicationStatus.choices]

        if new_status not in valid_statuses:
            return Response(
                {"error": f"'{new_status}' is not a valid status"},
                status=status.HTTP_400_BAD_REQUEST
            )

        application.status = new_status
        application.save()

        return Response(
            {"message": "Status updated", "status": application.status},
            status=status.HTTP_200_OK
        )