import unittest
from django.test import Client, TestCase


class SimpleTest(unittest.TestCase):
    def setUp(self):
        # user
        self.client = Client()

    def test_details(self):
        # go to home page
        response = self.client.get("/")

        # Check that the response is 200 OK.
        self.assertEqual(response.status_code, 200)