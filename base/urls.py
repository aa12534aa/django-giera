from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name=''),

    path('login-page', views.loginPage, name='login-page'),
    path('logout-page', views.logoutPage, name='logout-page'),
    path('regiser-page', views.registerPage, name='register-page'),

    path('lobby/<str:lobbyId>', views.joinLobby, name='join-lobby'),
    path('lobby/', views.createLobby, name='create-lobby'),
    path('game/<str:lobbyId>', views.startGame, name='startGame'),
    path('results/<str:lobbyId>', views.results, name='results')
]