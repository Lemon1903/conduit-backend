from django.urls import path

from . import views

urlpatterns = [
    path("sample/", views.SampleRoute.as_view(), name="sample"),
    path("protected/", views.SampleAuthenticatedRoute.as_view(), name="protected"),
    path("users/", views.Register.as_view(), name="register"),
    path("users/login/", views.Login.as_view(), name="login"),
    path("users/logout/", views.Logout.as_view(), name="logout"),
    path("users/refresh-token/", views.TokenRefresh().as_view(), name="refresh"),
]