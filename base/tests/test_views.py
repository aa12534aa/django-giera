import unittest
# SimpleTestCase działa bez bazy danych
from django.test import Client, TestCase, SimpleTestCase
from django.contrib import auth
from ..models import User, Lobby


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

# class RegisterLoginTest(unittest.TestCase):
#     def setUp(self):
#         self.client = Client()
#         User.objects.create(email="john3@gmail.com", username="john3", password="Smith")


#     def testDetails(self):
#         response = self.client.post("/register-page/", {"email": "john2@gmail.com", "username": "john123",  "password": "Smith", "password2": "Smith"})
#         self.assertEqual(response.status_code, 200)

#     def testOther(self):
#         self.client.post("/login-page/", {"email": "john@gmail.com", "password": "Smith"})
#         self.assertTrue("_auth_user_id" in self.client.session)

    # def testLogout(self):
        # user = auth.get_user(self.client)
        # self.assertTrue(user.is_authenticated())
        # self.client.post('/logout/')
        # self.assertEqual(user.is_authenticated(), False)