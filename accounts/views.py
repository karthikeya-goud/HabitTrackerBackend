from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from . import serializers
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView


class RegisterAPIView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = serializers.RegisterSerializers(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(status=status.HTTP_201_CREATED)
        except:
            return Response(
                {"message": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = serializers.CustomLoginSerializer
