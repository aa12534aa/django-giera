from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from . import functions
import json
import asyncio

# lobby handler
class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # get info about new player
        self.user = self.scope['user']
        await self.accept()


    async def receive(self, text_data):
        # get lobby id and command sent from frontend
        data = json.loads(text_data)
        self.lobbyId = data.get('lobbyId')
        value = data.get('value')

        if value == 'connecting':
            # if player refreshed the page and is no longer in lobby, redirect him to home
            isPlayerInLobby = await database_sync_to_async(functions.isPlayerInLobby)(self.user, self.lobbyId)
            if not isPlayerInLobby:
                await self.send(text_data=json.dumps(
                    {'type': 'kickPlayer'}
                ))
            
            # add this websocket connection to lobby group
            await self.channel_layer.group_add(
                f'lobby{self.lobbyId}', self.channel_name
                )
            
            # notify all players in lobby to update player list
            await self.channel_layer.group_send(
                f'lobby{self.lobbyId}',
                {"type": "getAllPlayers"}
            )

        elif value == 'kickPlayer':
            # when host kick player from lobby
            playerId = data.get('playerId')

            await self.channel_layer.group_send(
                f'lobby{self.lobbyId}',
                {
                    'type': 'kickPlayer',
                    'playerId': playerId
                }
            )

        elif value == 'startGame':
            """ send players info to move from lobby to game and set game time"""
            gameTime = data.get('time')
            await database_sync_to_async(functions.setLobbyTime)(self.lobbyId, gameTime)
            await self.channel_layer.group_send(
                f'lobby{self.lobbyId}',
                {'type': "startGame"}
            )

    async def getAllPlayers(self, event):
        """ get all players from lobby and send them for each player on frontend """
        players, host = await database_sync_to_async(functions.getPlayers)(self.lobbyId)
        lobby = await database_sync_to_async(functions.getLobby)(self.lobbyId)

        # inform new player if game is on and he has to wait
        if lobby.isActive:
            await self.send(text_data=json.dumps(
                {'type': 'gameIsOn'}
            ))
        else:
            await self.send(text_data=json.dumps(
                {'type': 'gameIsEnded'}
            ))

        await self.send(text_data=json.dumps(
            {
                "type": "players", 
                "players": players,
                'host': host
            }
        ))

    async def kickPlayer(self, event):
        """ kicking player by host """
        if event['playerId'] == self.user.id:
            await self.send(text_data=json.dumps(
                {'type': 'kickPlayer'}
            ))

    async def startGame(self, event):
        """ after start game change lobby and players to active """
        await database_sync_to_async(functions.startGame)(self.user, self.lobbyId)
        await self.send(text_data=json.dumps(
            {"type": 'startGame'}
        ))


    async def disconnect(self, code):
        # check if lobby is active
        lobby = await database_sync_to_async(functions.getLobby)(self.lobbyId)

        # if lobby is not active player left lobby otherwise game has started
        if not lobby.isActive:
            if (self.user.host is not None) and (str(self.user.host) == self.lobbyId):
                newHostId = await database_sync_to_async(functions.removeHost)(self.user, self.lobbyId)
                await self.channel_layer.group_send(
                    f'lobby{self.lobbyId}',
                    {
                        'type': 'newHost',
                        'newHostId': newHostId
                    }
                )

            else:
                await database_sync_to_async(functions.removePlayer)(self.user, self.lobbyId)

            await self.channel_layer.group_send(
                f'lobby{self.lobbyId}',
                {'type': 'getAllPlayers'}
            )

        await self.channel_layer.group_discard(
            f'lobby{self.lobbyId}', self.channel_name
        )

    async def newHost(self, event):
        # if user became a host then update him
        if self.user.id == event['newHostId']:
            self.user = await database_sync_to_async(functions.updateUser)(self.user)

        await self.send(text_data=json.dumps(
            {
                'type': 'newHost',
                'newHostId': event['newHostId']
            }
        ))


# game handler
class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # get info about player from lobby
        self.user = self.scope['user']
        await self.accept()

    async def receive(self, text_data):
        # get lobby id and command sent from frontend
        data = json.loads(text_data)
        self.lobbyId = data.get('lobbyId')
        value = data.get('value')

        if value == 'prepareGame':
            # get players and score to create score table
            playersAndScore = await database_sync_to_async(functions.getPlayersForGame)(self.lobbyId)

            # add this websocket connection to game group
            await self.channel_layer.group_add(
                f'game{self.lobbyId}', self.channel_name
            )

            await self.channel_layer.group_send(
                f'game{self.lobbyId}',
                {
                    'type': 'createScoreTable',
                    'playersAndScore': playersAndScore
                }
            )

        elif value == 'startTimer' and self.user.host is not None and str(self.user.host) == self.lobbyId:
            # take words to send them on frontend
            self.wordsList = await database_sync_to_async(functions.generateWords)()
            await self.channel_layer.group_send(
                f'game{self.lobbyId}',
                {
                    'type': 'prepareWords',
                    'wordsList': self.wordsList
                }
            )

            # run timer asynchronously so websocket is not blocked
            asyncio.create_task(self.startTimer())
        
        elif value == 'playerWord':
            word = data.get('word')
            # check if the word typed by the player is correct
            isCorrect, wordId = await database_sync_to_async(functions.checkWord)(self.user, self.lobbyId, word, self.wordsList)
            if isCorrect:
                # if correct send word info to frontend
                await self.send(text_data=json.dumps(
                    {
                        'type': 'correctWord',
                        'wordId': wordId
                    }
                ))

                await self.channel_layer.group_send(
                    f'game{self.lobbyId}',
                    {
                        'type': 'updateScoreTable',
                        'player': self.user.username
                    }
                )

    async def createScoreTable(self, event):
        await self.send(text_data=json.dumps(
            {
                'type': 'createScoreTable',
                'playersAndScore': event['playersAndScore']
            }
        ))

    async def updateScoreTable(self, event):
        """ inform other players about updated score """
        await self.send(text_data=json.dumps(
            {
                'type': 'updateScoreTable',
                'player': event['player']
            }
        ))

    async def prepareWords(self, event):
        """ send words to the frontend """
        self.wordsList = event['wordsList']
        await self.send(text_data=json.dumps(
            {
                'type': 'wordsForGame',
                'wordsList': event['wordsList'] 
            }
        ))

    async def startTimer(self):
        """ send all players each second updated game time """
        gameTimer = await database_sync_to_async(functions.getLobbyTime)(self.lobbyId)
        while gameTimer > 0:
            await self.channel_layer.group_send(
                f'game{self.lobbyId}',
                {
                    'type': 'sendTime',
                    'gameTimer': gameTimer
                }
            )
            gameTimer -= 1
            await asyncio.sleep(1)
        
        # after time passed end the game
        await database_sync_to_async(functions.deactivateLobby)(self.lobbyId)
        await self.channel_layer.group_send(
            f'game{self.lobbyId}',
            {'type': 'endGame'}
        )

    async def sendTime(self, event):
        await self.send(text_data=json.dumps(
            {
                'type': 'timer',
                'time': event['gameTimer']
            }
        ))

    async def endGame(self, event):
        """ send players info to move from game to lobby """
        await self.send(text_data=json.dumps(
            {
                'type': 'endGame',
                'lobbyId': self.lobbyId
            }
        ))

    
    async def disconnect(self, code):
        # check if lobby is active
        lobby = await database_sync_to_async(functions.getLobby)(self.lobbyId)

        # if lobby is active the player left lobby during game otherwise game has ended
        if lobby is not None and not lobby.isActive:
            await database_sync_to_async(functions.endGame)(self.user, self.lobbyId)

        elif self.user.host is not None and str(self.user.host) == self.lobbyId:
            await database_sync_to_async(functions.removeHost)(self.user, self.lobbyId)
            await self.channel_layer.group_send(
                f'game{self.lobbyId}',
                {'type': 'newHost'}
            )

        else:
            await database_sync_to_async(functions.removePlayer)(self.user, self.lobbyId)

        await self.channel_layer.group_discard(
                f'game{self.lobbyId}', self.channel_name
            )
        
    async def newHost(self, event):
        # if user became a host then update him
        self.user = await database_sync_to_async(functions.updateUser)(self.user)

# results handler
class ResultsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # get player info
        self.user = self.scope['user']
        await self.accept()

    async def receive(self, text_data):
        self.lobbyId = json.loads(text_data).get('lobbyId')
        print(self.lobbyId)

        await self.channel_layer.group_add(
            f'results{self.lobbyId}', self.channel_name
            )

        if self.user.host is not None and str(self.user.host) == self.lobbyId:
            asyncio.create_task(self.startTimer())

    async def startTimer(self):
        """ send all players each second updated results time """
        resultsTimer = 10
        while resultsTimer > 0:
            await self.channel_layer.group_send(
                f'results{self.lobbyId}',
                {
                    'type': 'sendTime',
                    'resultsTimer': resultsTimer
                }
            )
            resultsTimer -= 1
            await asyncio.sleep(1)

        await database_sync_to_async(functions.endResults)(self.lobbyId)

        await self.channel_layer.group_send(
            f'results{self.lobbyId}',
            {'type': 'backToLobby'}
        )

    async def sendTime(self, event):
        await self.send(text_data=json.dumps(
            {
                'type': 'timer',
                'time': event['resultsTimer']
            }
        ))

    async def backToLobby(self, event):
        await self.send(text_data=json.dumps(
            {
                'type': 'backToLobby',
                'lobbyId': self.lobbyId  
            }
        ))

    async def disconnect(self, code):
        # check if lobby is active
        lobby = await database_sync_to_async(functions.getLobby)(self.lobbyId)

        # if resutls is True the player left lobby during results otherwise game has ended
        if lobby.results:
            print(self.user)
            if self.user.host is not None and str(self.user.host) == self.lobbyId:
                await database_sync_to_async(functions.removeHost)(self.user, self.lobbyId)
                await self.channel_layer.group_send(
                    f'game{self.lobbyId}',
                    {'type': 'newHost'}
                )

            else:
                await database_sync_to_async(functions.removePlayer)(self.user, self.lobbyId)
        else:
            await database_sync_to_async(functions.backToLobby)(self.user, self.lobbyId)

        await self.channel_layer.group_discard(
                f'game{self.lobbyId}', self.channel_name
            )
        