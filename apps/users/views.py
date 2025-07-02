from django.shortcuts import get_object_or_404
from rest_framework.generics import RetrieveAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Profile
from .serializers import ProfileViewSerializer, ProfileViewUpdateSerializer


# Create your views here.
class ProfileView(RetrieveAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileViewSerializer
    authentication_classes = []

    def get_object(self):
        username = self.kwargs.get("username")
        profile = get_object_or_404(Profile, user__username=username)
        return profile


class ProfileRetrieveUpdate(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileViewUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        profile = get_object_or_404(Profile, user=user)
        return profile
