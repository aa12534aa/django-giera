from django.db import models
from django.core.exceptions import ValidationError
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

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(time__in=[30, 60, 90]),
                name="valid_lobby_time"
            ),
            models.CheckConstraint(
                condition=~models.Q(isActive=True, results=True),
                name="not_active_and_results_simultaneously"
            )
        ]

    def clean(self):
        if self.time != 30 or self.time != 60 or self.time != 90:
            raise ValidationError("Lobby time can only be 30, 60 or 90")

        if self.results and self.isActive:
            raise ValidationError("Lobby can't be active and in results at the same time")
    
class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lobby = models.ForeignKey(Lobby, on_delete=models.CASCADE)
    isPlaying = models.BooleanField(default=False)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(score__gte=0),
                name="Score_must_be_gt_zero"
            )
        ]

    def clean(self):
        if self.score < 0:
            raise ValidationError("Score can't be less than 0")