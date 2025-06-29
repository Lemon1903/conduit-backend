from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import RegisterSerializer, LoginSerializer, LogoutSerializer
from .models import User


class Home(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {
            "message": "Welcome to the Conduit API!",
            "user": request.user.username,
        }
        return Response(content)


class Register(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class Login(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if type(serializer.validated_data) is dict:
            user: User = serializer.validated_data["user"]
            refresh_token = RefreshToken.for_user(user)

            return Response(
                {
                    "access_token": str(refresh_token.access_token),
                    "refresh_token": str(refresh_token),
                    "username": user.username,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {"detail": "Invalid data structure."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class Logout(GenericAPIView):
    serializer_class = LogoutSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
