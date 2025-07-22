from django.urls import path

from . import views


urlpatterns = [
    path(
        "profiles/<str:username>/",
        views.ProfileView.as_view(),
        name="profile-view",
    ),
    path(
        "profiles/<str:username>/follow/",
        views.FollowUnfollowProfileView.as_view(),
        name="profile-follow",
    ),
    path(
        "user/", views.OwnProfileRetrieveUpdate.as_view(), name="profile-update"
    ),
]
