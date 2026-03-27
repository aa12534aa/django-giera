import unittest
# SimpleTestCase działa bez bazy danych
from django.test import Client, TestCase, SimpleTestCase
from django.contrib import auth
from ..models import User, Lobby, Player
from django.urls import reverse
from channels.testing import WebsocketCommunicator
from giera.asgi import application
import json
import asyncio

class JoinAndDisconnectLobbyTest(TestCase):
    def setUp(self):
        self.lobby = Lobby.objects.create()
        self.user1 = User.objects.create_user(email="john1@gmail.com", username="john1", password="Smith", host=self.lobby.id)
        self.user2 = User.objects.create_user(email="john2@gmail.com", username="john2", password="Smith")
        self.player1 = Player.objects.create(lobby=self.lobby, user=self.user1)
        self.player2 = Player.objects.create(lobby=self.lobby, user=self.user2)

    def connectToWS(self, user):
        connection = WebsocketCommunicator(
            application,
            "/ws/joinLobby/"
        )
        connection.scope['user'] = user
        return connection
    
    async def addToWsLayer(self, connection):
        await connection.send_to(text_data=json.dumps({
            'value': 'connecting',
            'lobbyId': self.lobby.id
        }))
    
    async def getMessages(self, connection):
        messages = []
        while True:
            try:
                response = await asyncio.wait_for(connection.receive_from(), timeout=0.2)
                messages.append(json.loads(response))
            except asyncio.TimeoutError:
                break
        return messages
    
    async def testConnectionToWs(self):
        connection = self.connectToWS(self.user1)
        connected, _ = await connection.connect()
        self.assertTrue(connected)

    async def testAddPlayerToWsLayerAndShowPlayersList(self):
        connection1 = self.connectToWS(self.user1)
        await connection1.connect()
        connection2 = self.connectToWS(self.user2)
        await connection2.connect()

        await self.addToWsLayer(connection1)
        await self.addToWsLayer(connection2)

        response1 = await self.getMessages(connection1)
        response2 = await self.getMessages(connection2)

        self.assertEqual(response1[1]['type'], 'players')
        self.assertEqual(len(response1[1]['players']), 2)
        self.assertEqual(response2[1]['type'], 'players')
        self.assertEqual(len(response2[1]['players']), 2)

    async def testShowHostProperly(self):
        connection1 = self.connectToWS(self.user1)
        await connection1.connect()
        connection2 = self.connectToWS(self.user2)
        await connection2.connect()

        await self.addToWsLayer(connection1)
        await self.addToWsLayer(connection2)

        response1 = await self.getMessages(connection1)
        response2 = await self.getMessages(connection2)
        self.assertEqual(response1[1], response2[1])

        for player in response2[1]['players']:
            if player['username'] == self.user1.username:
                self.assertTrue(player['isHost'])
            else:
                self.assertFalse(player['isHost'])

    async def testDisconnectionFromLobby(self):
        connection1 = self.connectToWS(self.user1)
        await connection1.connect()
        connection2 = self.connectToWS(self.user2)
        await connection2.connect()

        await self.addToWsLayer(connection1)
        await self.addToWsLayer(connection2)

        await self.getMessages(connection1)
        await self.getMessages(connection2)

        await connection2.disconnect()
        response1 = await self.getMessages(connection1)
        self.assertEqual(len(response1[1]['players']), 1)
    
    async def testHostDisconnectionFromLobby(self):
        connection1 = self.connectToWS(self.user1)
        await connection1.connect()
        connection2 = self.connectToWS(self.user2)
        await connection2.connect()

        await self.addToWsLayer(connection1)
        await self.addToWsLayer(connection2)

        await self.getMessages(connection1)
        await self.getMessages(connection2)

        await connection1.disconnect()
        response2 = await self.getMessages(connection2)
        self.assertEqual(len(response2[-1]['players']), 1)
        self.assertTrue(response2[-1]['players'][0]['isHost'])