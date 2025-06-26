from click import password_option
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

from .utils import generate_verification_link

User = get_user_model()


class RequestPasswordResetView(APIView):
    def post(self, request):
        email = request.data.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = f"http://localhost:8000/reset-password/?uid={uid}&token={token}"

            send_mail(
                subject="🔐 Password Reset",
                message=f"Reset your password using the following link:\n\n{reset_link}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
        return Response({"message": "If an account with this email exists, a reset link was sent."}, status=status.HTTP_200_OK)


class ConfirmPasswordResetView(APIView):
    def post(self, request):
        uid = request.data.get("uid")
        token = request.data.get("token")
        new_password = request.data.get("new_password")

        try:
            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"error": "Invalid link."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Token is invalid or expired."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"message": "Password has been reset."}, status=status.HTTP_200_OK)


class RegisterView(APIView):
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        data = request.data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            role=data.get('role', 'applicant'),
        )
        user.is_active = True
        user.save()

        link = generate_verification_link(request, user)

        send_mail(
            subject="Verify your JobBoard account",
            message=f"Click to verify your account: {link}",
            from_email="noreply@jobboard.com",
            recipient_list=[user.email],
        )

        return Response({"message": "User created. Please check your email to verify your account."}, status=201)


class VerifyEmailView(APIView):
    def get(self, request):
        uidb64 = request.query_params.get('uid')
        token = request.query_params.get('token')

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except Exception:
            return Response({"error": "Invalid link"}, status=400)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token"}, status=400)

        user.is_email_verified = True
        user.save()
        return Response({"message": "Email verified!"}, status=200)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get('password')

        user = get_object_or_404(User, email=email)

        if not user.check_password(password):
            return Response({"error": "Invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)
        return Response({
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        })