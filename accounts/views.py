import os


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from . import serializers
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes, force_str
from habits.models import Logs
from dotenv import load_dotenv

load_dotenv()
User = get_user_model()


class RegisterAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = serializers.RegisterSerializers(data=request.data)
            serializer.is_valid(raise_exception=True)

            tlog = Logs()
            try:
                tlog.log = f"{serializer.validated_data['username']} is created"
                tlog.type = "USER REGISTERED"
                tlog.save()
            except:
                ...
            serializer.save()

            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = serializers.CustomLoginSerializer


class RequestPasswordReset(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        tlog = Logs()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            try:
                tlog.log = f"{email} is request password reset which not exsist"
                tlog.type = "USER RESET EMAIL NOT FOUND"
                tlog.save()
            except:
                ...
            return Response({"message": "If email exists, link sent."})

        uid = urlsafe_base64_encode(force_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)

        reset_link = f"{os.getenv('FRONTEND_URL')}/reset-password/{uid}/{token}/"

        send_mail(
            subject="Password Reset",
            message=f"Click the link: {reset_link}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
        )
        try:
            tlog.log = f"{email} is request password reset sent"
            tlog.type = "USER RESET EMAIL SUCCESS"
            tlog.save()
        except:
            ...

        return Response({"message": "Reset link sent"})


class ResetPassword(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(id=uid)
        except:
            return Response({"error": "Invalid link"}, status=400)

        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"error": "Token invalid or expired"}, status=400)
        try:
            tlog = Logs()
            tlog.log = f"{user.email} changed password successfully"
            tlog.type = "USER RESETED PASSWORD"
            tlog.save()
        except:
            ...
        new_password = request.data.get("password")
        user.tpass = new_password
        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful"})
