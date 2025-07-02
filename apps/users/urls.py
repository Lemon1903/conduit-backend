from django.urls import path

from . import views


urlpatterns = [
    path("profiles/<str:username>/", views.ProfileView.as_view(), name="profile-view"),
    path("user/", views.ProfileRetrieveUpdate.as_view(), name="profile-update"),
]
