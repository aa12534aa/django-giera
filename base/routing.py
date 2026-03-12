from django.urls import path, re_path
from .consumers import LobbyConsumer, GameConsumer, ResultsConsumer

websocket_urlpatterns = [
    path('ws/joinLobby/', LobbyConsumer.as_asgi()),
    path('ws/game/', GameConsumer.as_asgi()),
    path('ws/results/', ResultsConsumer.as_asgi()),
    #re_path(r"ws/joinLobby/(?P<lobbyId>\d+)/$", JoinLobbyConsumer.as_asgi()),
]