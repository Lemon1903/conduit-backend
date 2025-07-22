from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Profile
from .serializers import ProfileViewSerializer, OwnProfileViewUpdateSerializer


# Used Generics instead of ViewSets for learning purposes
# This is to understand how to create API views using different methods


# Create your views here.
class ProfileView(RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileViewSerializer
    # This could be used for a route like: /profiles/<username>/
    # lookup_field = 'user__username'
    # lookup_url_kwarg = 'username'

    # Used this way for learning purposes, to understand different retrieval methods
    def get_object(self):
        username = self.kwargs.get("username")
        profile = get_object_or_404(Profile, user__username=username)
        return profile


class FollowUnfollowProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, **kwargs):
        user = request.user
        other_profile = get_object_or_404(
            Profile, user__username=kwargs.get("username")
        )
        other_profile.followers.add(getattr(user, "profile"))
        return Response(
            {"detail": f"You are now following {other_profile.user.username}"},
            status=status.HTTP_200_OK,
        )

    def delete(self, request, **kwargs):
        user = request.user
        other_profile = get_object_or_404(
            Profile, user__username=kwargs.get("username")
        )
        other_profile.followers.remove(getattr(user, "profile"))
        return Response(
            {"detail": f"You have unfollowed {other_profile.user.username}"},
            status=status.HTTP_200_OK,
        )


class OwnProfileRetrieveUpdate(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = OwnProfileViewUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        profile = get_object_or_404(Profile, user=user)
        return profile
