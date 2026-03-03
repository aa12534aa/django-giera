from django.contrib import admin
from .models import User, Lobby, Player

# Register your models here.
admin.register(User)
admin.register(Lobby)
admin.register(Player)