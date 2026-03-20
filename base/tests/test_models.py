import unittest
from django.test import Client, TestCase
from django.core.exceptions import ValidationError
from ..models import User, Lobby, Player
from django.db import IntegrityError

class UserModelTest(TestCase):

    def setUp(self):
        self.user = User(username='john', email='john@gmail.com', password="john123")
    
    def testUserObjectName(self):
        self.assertEqual(str(self.user), 'john@gmail.com')


class LobbyModelTest(TestCase):

    # za pomocą tej classmethod w testach tworzymy cls.lobby tylko raz, a w samym setUp tworzymy self.lobby tyle razy ile mamy testów + 1
    @classmethod
    def setUpTestData(cls):
        cls.lobby = Lobby(isActive=True, results=False)
    
    def testLobbyTime(self):
        self.assertEqual(self.lobby.time, 30)

        self.lobby.time = 0
        with self.assertRaises(ValidationError):
            self.lobby.clean()

    def testLobbyActiveAndResultsConflict(self):
        self.assertFalse(self.lobby.results)
        self.lobby.results = True
        with self.assertRaises(ValidationError):
            self.lobby.clean()
    
    def testLobbyActiveAndResultsConflictConstraint(self):
        lobby = Lobby(isActive=True, results=True)
        with self.assertRaises(IntegrityError):
            lobby.save()

    def testLobbyTimeConstraint(self):
        lobby = Lobby(isActive=True, results=False, time=25)
        with self.assertRaises(IntegrityError):
            lobby.save()


class PlayerModelTest(TestCase):
    
    def setUp(self):
        self.user = User(username='john', email='john@gmail.com', password="john123")
        self.lobby = Lobby(id=1, isActive=True, results=False)
        self.user.host = self.lobby.id
        self.player = Player(user=self.user, lobby=self.lobby)

    def testPlayerObjectName(self):
        self.assertEqual(str(self.player), self.user.username)

    def testDefaultPlayersettings(self):
        self.assertFalse(self.player.isPlaying)
        self.assertEqual(self.player.score, 0)

    def testLobbyHostingInUser(self):
        self.assertEqual(self.player.user.host, self.player.lobby.id)

    def testScoreSubZero(self):
        self.player.score -= 1
        with self.assertRaises(ValidationError):
            self.player.clean()

    def testScoreSubZeroConstraint(self):
        self.user.save()
        self.lobby.save()
        player = Player(user=self.user, lobby=self.lobby, score=-2)
        with self.assertRaises(IntegrityError):
            player.save()