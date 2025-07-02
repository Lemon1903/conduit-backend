from django.conf import settings
from django.db import models


# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    followers = models.ManyToManyField(
        "self",
        related_name="following",
        blank=True,
        symmetrical=False,
    )

    def __str__(self):
        return self.user.username
