from .models import User, Lobby, Player
import random

# views
def createLobby(user):
    lobby = Lobby.objects.create()
    Player.objects.create(user=user, lobby=lobby)
    user.host = lobby.id
    user.save()
    return lobby.id

def lobbyExists(lobbyId):
    try:
        Lobby.objects.get(id=lobbyId)
        return True
    except:
        return False
    
def getAllLobbies():
    lobbies = Lobby.objects.all()
    lobbyList = []
    for lobby in lobbies:
        lobbyList.append({'id': lobby.id, 'isActive': lobby.isActive})
    return lobbyList


# Lobby functions
def addPlayerToLobby(user, lobbyId):
    lobby = Lobby.objects.get(id=lobbyId)
    player, _ = Player.objects.get_or_create(user=user, lobby=lobby)
    return player

def isPlayerInLobby(user, lobbyId):
    try:
        Player.objects.get(user=user, lobby=lobbyId)
        return True
    except:
        return False

def getPlayers(lobbyId):
    if not lobbyExists(lobbyId):
        return [[], '']
    lobby = Lobby.objects.get(id=lobbyId)
    players = Player.objects.filter(lobby=lobby)
    playersArray = []
    host = None
    for p in players:
        if p.user.host is not None and str(p.user.host) == lobbyId:
            playersArray.append({'username': p.user.username, 'id': p.user.id, 'isHost': True})
            host = p.user.id
        else:
            playersArray.append({'username': p.user.username, 'id': p.user.id, 'isHost': False})
    return [playersArray, host]


# Game functions
def startGame(user, lobbyId):
    lobby = Lobby.objects.get(id=lobbyId)
    player = Player.objects.get(user=user, lobby=lobby)
    player.isPlaying = True
    player.save()
    if not lobby.isActive:
        lobby.isActive = True
        lobby.save()

def deactivateLobby(lobbyId):
    try:
        lobby = Lobby.objects.get(id=lobbyId)
    except:
        return None
    lobby.isActive = False
    lobby.save()

def checkWord(user, lobbyId, word, wordsList):
    player = Player.objects.get(user=user, lobby=lobbyId)
    wordId = player.score
    if wordsList[wordId] == word:
        player.score += 1
        player.save()
        return [True, str(wordId)]
    else:
        return [False, str(wordId)]

def generateWords():
    with open("E:\\praca\\django\\giera\\base\\words-base\\The Oxford 5000.txt", "r") as f:
        words = f.read()
    wordsList = random.choices(words.split('\n')[:-1], k=200)
    return wordsList

def endGame(user, lobbId):
    try:
        lobby = Lobby.objects.get(id=lobbId)
    except:
        lobby = None
    if lobby is not None:
        player = Player.objects.get(user=user, lobby=lobby)
        player.isPlaying = False
        player.save()
        return lobby    


# Lobby and Game functions
def getLobby(lobbyId):
    lobby = Lobby.objects.get(id=lobbyId)
    return lobby

def removePlayer(user, lobbyId):
    try:
        lobby = Lobby.objects.get(id=lobbyId)
    except:
        lobby = None
    if lobby is not None:
        player = Player.objects.get(user=user, lobby=lobby)
        player.delete()

def removeHost(user, lobbyId):
    user.host = None
    user.save()
    lobby = Lobby.objects.get(id=lobbyId)
    player = Player.objects.get(user=user, lobby=lobby)
    player.delete()
    players = Player.objects.filter(lobby=lobby)
    if len(players) > 0:
        newHost = User.objects.get(id=players[0].user.id)
        newHost.host = lobbyId
        newHost.save()
        return newHost.id
    else:
        lobby.delete()

def updateUser(user):
    user = User.objects.get(id=user.id)
    return user