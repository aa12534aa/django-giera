from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from . import functions
import json
import asyncio
from .models import Lobby

# Lobby handler
class LobbyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.gameStarted = False
        await self.accept()


    async def receive(self, text_data):
        self.lobbyId = json.loads(text_data).get('lobbyId')
        value = json.loads(text_data).get('value')

        if value == 'connecting':
            isPlayerInLobby = await database_sync_to_async(functions.isPlayerInLobby)(self.user, self.lobbyId)
            if not isPlayerInLobby:
                await self.send(text_data=json.dumps(
                    {'type': 'kickPlayer'}
                ))
            
            await self.channel_layer.group_add(
                f'lobby{self.lobbyId}', self.channel_name
                )
            
            await self.channel_layer.group_send(
                f'lobby{self.lobbyId}',
                {"type": "getAllPlayers"}
            )

        elif value == 'startGame':
            await self.channel_layer.group_send(
                f'lobby{self.lobbyId}',
                {'type': "startGame"}
            )

        elif value == 'kickPlayer':
            playerId = json.loads(text_data).get('playerId')
            print(playerId, 'XDDD')

            await self.channel_layer.group_send(
                f'lobby{self.lobbyId}',
                {
                    'type': 'kickPlayer',
                    'playerId': playerId
                }
            )

    async def getAllPlayers(self, event):
        players, host = await database_sync_to_async(functions.getPlayers)(self.lobbyId)
        lobby = await database_sync_to_async(functions.getLobby)(self.lobbyId)
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
        if event['playerId'] == self.user.id:
            await self.send(text_data=json.dumps(
                {'type': 'kickPlayer'}
            ))

    async def startGame(self, event):
        self.gameStarted = True
        await self.send(text_data=json.dumps(
            {"type": 'startGame'}
        ))


    async def disconnect(self, code):
        if (self.user.host is not None) and (str(self.user.host) == self.lobbyId):
            if not self.gameStarted:
                newHostId = await database_sync_to_async(functions.removeHost)(self.user, self.lobbyId)
                await self.channel_layer.group_send(
                    f'lobby{self.lobbyId}',
                    {
                        'type': 'newHost',
                        'newHostId': newHostId
                    }
                )
        else:
            if not self.gameStarted:
                await database_sync_to_async(functions.removePlayer)(self.user, self.lobbyId)

        await self.channel_layer.group_send(
            f'lobby{self.lobbyId}',
            {'type': 'getAllPlayers'}
        )

        await self.channel_layer.group_discard(
            f'lobby{self.lobbyId}', self.channel_name
        )

    async def newHost(self, event):
        self.user = await database_sync_to_async(functions.updateUser)(self.user)

        await self.send(text_data=json.dumps(
            {
                'type': 'newHost',
                'newHostId': event['newHostId']
            }
        ))


# Game handler
class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        await self.accept()

    async def receive(self, text_data):
        self.lobbyId = json.loads(text_data).get('lobbyId')
        value = json.loads(text_data).get('value')

        if value == 'prepareGame':
            await database_sync_to_async(functions.startGame)(self.user, self.lobbyId)

            await self.channel_layer.group_add(
                f'game{self.lobbyId}', self.channel_name
            )

        elif value == 'startTimer' and self.user.host is not None and str(self.user.host) == self.lobbyId:
            self.wordsList = await database_sync_to_async(functions.generateWords)()
            await self.channel_layer.group_send(
                f'game{self.lobbyId}',
                {
                    'type': 'prepareWords',
                    'wordsList': self.wordsList
                }
            )
            asyncio.create_task(self.startTimer())
        
        elif value == 'playerWord':
            word = json.loads(text_data).get('word')
            isCorrect, wordId = await database_sync_to_async(functions.checkWord)(self.user, self.lobbyId, word, self.wordsList)
            if isCorrect:
                await self.send(text_data=json.dumps(
                    {
                        'type': 'correctWord',
                        'wordId': wordId
                    }
                ))
            else:
                print('xd')

    async def prepareWords(self, event):
        await self.send(text_data=json.dumps(
            {
                'type': 'wordsForGame',
                'wordsList': event['wordsList'] 
            }
        ))

    async def startTimer(self):
        gameTimer = 30
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
        await self.send(text_data=json.dumps(
            {
                'type': 'endGame',
                'lobbyId': self.lobbyId
            }
        ))

    
    async def disconnect(self, code):
        # Checking if player left game or game has ended
        lobby = await database_sync_to_async(functions.getLobby)(self.lobbyId)

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
        self.user = await database_sync_to_async(functions.updateUser)(self.user)