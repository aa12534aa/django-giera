from .models import User, Lobby, Player
import random

## views
def createLobby(user):
    """ create lobby and set the host """
    lobby = Lobby.objects.create()
    Player.objects.create(user=user, lobby=lobby)
    user.host = lobby.id
    user.save()
    return lobby.id

def lobbyExists(lobbyId):
    """ check if lobby with given ID exists """
    try:
        Lobby.objects.get(id=lobbyId)
        return True
    except Lobby.DoesNotExists:
        return False

def getAllLobbies():
    """ get lobbies to display them on the home page """
    lobbies = Lobby.objects.all()
    lobbyList = []
    for lobby in lobbies:
        lobbyList.append({'id': lobby.id, 'isActive': lobby.isActive})
    return lobbyList

def addPlayerToLobby(user, lobbyId):
    lobby = Lobby.objects.get(id=lobbyId)
    player, _ = Player.objects.get_or_create(user=user, lobby=lobby)
    return player

def getScoreTable(lobbyId):
    players = Player.objects.filter(lobby=lobbyId)
    results = []
    for player in players:
        results.append({'username': player.user.username, 'score': player.score})
    return results


## Lobby functions
def isPlayerInLobby(user, lobbyId):
    """ check if player with given user and lobby exists """
    try:
        Player.objects.get(user=user, lobby=lobbyId)
        return True
    except:
        return False
    
def getPlayers(lobbyId):
    """ get all players from lobby and return them """
    if not lobbyExists(lobbyId):
        return [[], '']
    lobby = Lobby.objects.get(id=lobbyId)
    players = Player.objects.filter(lobby=lobby)
    playersArray = []
    host = None
    for p in players:
        # host
        if p.user.host is not None and str(p.user.host) == lobbyId:
            playersArray.append({'username': p.user.username, 'id': p.user.id, 'isHost': True})
            host = p.user.id
        # normal player
        else:
            playersArray.append({'username': p.user.username, 'id': p.user.id, 'isHost': False})
    return [playersArray, host]

def startGame(user, lobbyId):
    """ start game and change lobby and players states to active (all players use this function) """
    lobby = Lobby.objects.get(id=lobbyId)
    player = Player.objects.get(user=user, lobby=lobby)
    player.isPlaying = True
    player.save()
    if not lobby.isActive:
        lobby.isActive = True
        lobby.save()

def setLobbyTime(lobbyId, gameTime):
    lobby = Lobby.objects.get(id=lobbyId)
    lobby.time = gameTime
    lobby.save()


## Game functions
def getLobbyTime(lobbyId):
    lobby = Lobby.objects.get(id=lobbyId)
    return lobby.time

def getPlayersForGame(lobbyId):
    """ get players to create the game score table """
    players = Player.objects.filter(lobby=lobbyId)
    playersAndScore = []
    for p in players:
        playersAndScore.append({'username': p.user.username, 'score': p.score})
    return playersAndScore

def deactivateLobby(lobbyId):
    """ after the game check if lobby exists and deactivate it """
    try:
        lobby = Lobby.objects.get(id=lobbyId)
    except:
        return None
    lobby.isActive = False
    lobby.results = True
    lobby.save()

def checkWord(user, lobbyId, word, wordsList):
    """ check if player typed the correct word, add points to player and return word """
    player = Player.objects.get(user=user, lobby=lobbyId)
    wordId = player.score
    if wordsList[wordId] == word:
        player.score += 1
        player.save()
        return [True, str(wordId)]
    else:
        return [False, str(wordId)]

def generateWords():
    """ get random 200 words for whole players in lobby and return them """
    with open("E:\\praca\\django\\giera\\base\\words-base\\The Oxford 5000.txt", "r") as f:
        words = f.read()
    wordsList = random.choices(words.split('\n')[:-1], k=200)
    return wordsList

def endGame(user, lobbId):
    """ after the game reset player state and score """
    try:
        lobby = Lobby.objects.get(id=lobbId)
    except:
        lobby = None
    if lobby is not None:
        player = Player.objects.get(user=user, lobby=lobby)
        player.isPlaying = False
        player.score = 0
        player.save()
        return lobby    


## Lobby and Game functions
def getLobby(lobbyId):
    """ get lobby to check if it is active """
    lobby = Lobby.objects.get(id=lobbyId)
    return lobby

def removePlayer(user, lobbyId):
    """ remove player from lobby when he leaves """
    try:
        lobby = Lobby.objects.get(id=lobbyId)
    except:
        lobby = None
    if lobby is not None:
        player = Player.objects.get(user=user, lobby=lobby)
        player.delete()

def removeHost(user, lobbyId):
    """ remove host from lobby when he leaves and give host to other player """
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
    """ after host change we update users to be sure who is new host"""
    user = User.objects.get(id=user.id)
    return user


## Results
def endResults(lobbyId):
    lobby = Lobby.objects.get(id=lobbyId)
    lobby.results = False
    lobby.save()

def backToLobby(user, lobbyId):
    player = Player.objects.get(user=user, lobby=lobbyId)
    player.score = 0
    player.save()