from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=200, unique=True)
    email = models.EmailField(unique=True)
    host = models.IntegerField(null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    
class Lobby(models.Model):
    isActive = models.BooleanField(default=False)
    results = models.BooleanField(default=False)
    time = models.IntegerField(default=30)
    
class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    isPlaying = models.BooleanField(default=False)
    score = models.IntegerField(default=0)