from django.shortcuts import render, redirect
from .forms import UserForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import functions


def index(request):
    return render(request, 'index.html')



def home(request):
    lobbies = functions.getAllLobbies()
    context = {'lobbies': lobbies}
    return render(request, 'home.html', context) 

def loginPage(request):
    pageType = 'login'
    if request.method == 'POST':
        email = request.POST["email"].lower()
        password = request.POST["password"]
        user = authenticate(request, username=email, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('')
        else:
            messages.error(request, 'username or password not correct')
    context = {'pageType': pageType}
    return render(request, 'login-register.html', context)

def registerPage(request):
    form = UserForm()
    pageType = 'register'

    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.save()
            login(request, user)
            return redirect('')


    context = {'pageType': pageType, 'form': form}
    return render(request, 'login-register.html', context)

@login_required
def logoutPage(request):
    logout(request)
    return render(request, 'home.html') 

def createLobby(request):
    if request.user.is_authenticated:
        lobbyId = functions.createLobby(request.user)
        functions.addPlayerToLobby(request.user, lobbyId)
        return redirect(f'/lobby/{str(lobbyId)}')
    else:
        messages.error(request, 'you must be logged in to join or create lobby')
        return redirect('')

def joinLobby(request, lobbyId):
    if request.user.is_authenticated:
        if functions.lobbyExists(lobbyId):
            functions.addPlayerToLobby(request.user, lobbyId)
            context = {'lobbyId': lobbyId}
            return render(request, 'lobby.html', context)
        else:
            messages.error(request, f'The lobby {lobbyId} doesnt exists')
            return redirect('')
    else:
        messages.error(request, 'you must be logged in to join or create lobby')
        return redirect('')
    
def startGame(request, lobbyId):
    context = {'lobbyId': lobbyId}
    return render(request, 'game.html', context)