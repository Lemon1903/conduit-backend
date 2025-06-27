from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # No password field as AbstractUser already includes it
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    bio = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email