from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Application, AutoResponse
from .serializers import ApplicationSerializer
from api.permissions import IsApplicant, IsRecruiter, IsEmailVerified
from notifications.tasks import send_application_status_email
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser


class ApplicationViewSet(viewsets.ModelViewSet):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = ApplicationSerializer
    queryset = Application.objects.all()

    def get_permissions(self):
        if self.action == "update_status":
            return [IsRecruiter(), IsEmailVerified()]
        elif self.action == "create":
            return [IsApplicant(), IsEmailVerified()]
        return [permissions.IsAuthenticated(), IsEmailVerified()]

    def get_queryset(self):
        user = self.request.user
        if user.is_applicant():
            return Application.objects.filter(applicant=user)
        elif user.is_recruiter():
            return Application.objects.filter(job__company__owner=user)
        return Application.objects.none()

    def perform_create(self, serializer):
        application = serializer.save(applicant=self.request.user)
        job = application.job

        try:
            auto = AutoResponse.objects.get(job=job, event="on_apply")
            subject = auto.subject
            message = auto.body
        except AutoResponse.DoesNotExist:
            subject = f"Thanks for applying to {job.title}!"
            message = (
                f"Hi {application.applicant.username},\n\n"
                f"Thanks for applying to '{job.title}' at {job.company.name}.\n"
                "We'll review your application and get back to you soon!"
            )

        send_application_status_email.delay(
            to_email=application.applicant.email,
            subject=subject,
            message=message
        )

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

        # Load AutoResponse
        try:
            auto = AutoResponse.objects.get(job=application.job, event="on_status_change")
            subject = auto.subject
            message = auto.body
        except AutoResponse.DoesNotExist:
            subject = f"Your application status has been updated to {new_status.title()}"
            message = (
                f"Hi {application.applicant.username},\n\n"
                f"The status of your application for '{application.job.title}' has been changed to '{new_status}'."
            )

        send_application_status_email.delay(
            to_email=application.applicant.email,
            subject=subject,
            message=message
        )

        return Response(
            {"message": "Status updated", "status": application.status},
            status=status.HTTP_200_OK
        )