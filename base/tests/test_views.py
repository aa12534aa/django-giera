import unittest
# SimpleTestCase działa bez bazy danych
from django.test import Client, TestCase, SimpleTestCase
from django.contrib import auth
from ..models import User, Lobby, Player
from django.urls import reverse


class HomePageTest(TestCase):

    def setUp(self):
        Lobby.objects.create(id=1)
        Lobby.objects.create(id=2)

    def testHomePageTemplate(self):
        response = self.client.get("/")
        self.assertTemplateUsed(response, "home.html")

    def testHomePageButtons(self):
        response = self.client.get("/")
        self.assertContains(response, "Log in/Register", status_code=200)
        self.assertContains(response, "Join Lobby")
        self.assertContains(response, "Create Lobby")

    def testHomePageLobbiesTable(self):
        response = self.client.get("/")
        self.assertEqual(len(response.context['lobbies']), 2)
        self.assertContains(response, "1")
        self.assertContains(response, "2")
        self.assertNotContains(response, "There is no lobby here")

    def testHomePageWithoutLobbies(self):
        Lobby.objects.all().delete()
        response = self.client.get("/")
        self.assertContains(response, "There is no lobby here")

class RegisterLoginLogoutPageTest(TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create_user(email="john3@gmail.com", username="john3", password="Smith")

    def testLoginPageAndLogout(self):
        response = self.client.post("/login-page/", {"email": "john3@gmail.com", "password": "Smith"})
        # 302 znaczy, że przeszliśmy na inną strone
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)

        self.client.get("/logout-page/")
        self.assertFalse('_auth_user_id' in self.client.session)
        # sprawdzamy, czy w url znajduję się ''
        self.assertIn('', response.url)

    def testRegisterPage(self):
        response = self.client.post("/register-page/", {"email": "john123@gmail.com", "username": "john123", "password1": "Smith123xd", "password2": "Smith123xd"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue('_auth_user_id' in self.client.session)
        self.assertIn('', response.url)
        self.assertTrue(User.objects.get(username='john123'))

    def testLogoutWithoutLogin(self):
        response = self.client.get("/logout-page/")
        # przejście, że po zalogowaniu możemy się wylogować
        self.assertRedirects(response, expected_url=f"/login-page/?next=/logout-page/")
        # self.assertEqual(response.status_code, 302)
        # self.assertIn('/login-page/', response.url)


class CreatingJoiningLobbyTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.client2 = Client()

        User.objects.create_user(email="john1@gmail.com", username="john1", password="Smith")
        User.objects.create_user(email="john2@gmail.com", username="john2", password="Smith")

        self.client.post('/login-page/', {'email': 'john1@gmail.com', 'password': 'Smith'})
        self.client2.post('/login-page/', {'email': 'john2@gmail.com', 'password': 'Smith'})


    def testCreateLobby(self):
        response = self.client.get(reverse('create-lobby'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lobby.html')
        self.assertContains(response, "Go Home")

        lobby = Lobby.objects.first()
        user1 = User.objects.get(email='john1@gmail.com')
        self.assertContains(response, f"Lobby: {lobby.id}")
        self.assertEqual(lobby.id, user1.host)

        players = Player.objects.filter(lobby=lobby)
        self.assertEqual(players.count(), 1)

    def testJoinLobby(self):
        self.client.get(reverse('create-lobby'), follow=True)
        lobby = Lobby.objects.first()

        response = self.client2.get(f'/lobby/{lobby.id}', follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lobby.html')
        self.assertContains(response, "Go Home")
        self.assertContains(response, f"Lobby: {lobby.id}")

        user2 = User.objects.get(email='john2@gmail.com')
        self.assertNotEqual(lobby.id, user2.host)

        players = Player.objects.filter(lobby=lobby)
        self.assertEqual(players.count(), 2)

    def testCreateLobbyWithoutLogin(self):
        self.client.get('/logout-page/')
        self.assertFalse('_auth_user_id' in self.client.session)

        response = self.client.get(reverse('create-lobby'), follow=True)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, "you must be logged in to join or create lobby")

    def testJoinLobbyWithoutLogin(self):
        self.client.get('/logout-page/')
        self.assertFalse('_auth_user_id' in self.client.session)

        response = self.client.get('/lobby/1', follow=True)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, "you must be logged in to join or create lobby")

    def testJoinToNotExistentLobby(self):
        response = self.client.get('/lobby/1', follow=True)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, "The lobby 1 doesnt exists")