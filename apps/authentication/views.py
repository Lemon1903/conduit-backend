from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer, LoginSerializer
from .models import User


class SampleRoute(APIView):
    authentication_classes = []

    def get(self, request):
        content = {"message": "This is a sample unauthenticated route."}
        return Response(content)


class SampleAuthenticatedRoute(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        content = {
            "message": "This is an authenticated route.",
            "user": request.user.username,
        }
        return Response(content)


class Register(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    authentication_classes = []


class Login(GenericAPIView):
    serializer_class = LoginSerializer
    authentication_classes = []

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if type(serializer.validated_data) is not dict:
            return Response(
                "Invalid data structure.", status=status.HTTP_400_BAD_REQUEST
            )

        user: User = serializer.validated_data["user"]
        refresh_token = RefreshToken.for_user(user)

        response = Response(
            {
                "access_token": str(refresh_token.access_token),
                "username": user.username,
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh_token),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="None" if not settings.DEBUG else "Lax",
            max_age=60 * 60 * 24 * 7,  # 7 days in seconds
        )

        return response


class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                "Refresh token not found.", status=status.HTTP_400_BAD_REQUEST
            )

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError:
            return Response("Bad token.", status=status.HTTP_400_BAD_REQUEST)

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie("refresh_token")
        return response


class TokenRefresh(APIView):
    authentication_classes = []

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                "Refresh token not found.", status=status.HTTP_400_BAD_REQUEST
            )

        try:
            new_token = RefreshToken(refresh_token)
            return Response(
                {"access_token": str(new_token.access_token)},
                status=status.HTTP_200_OK,
            )
        except:
            return Response("Bad token", status=status.HTTP_400_BAD_REQUEST)
