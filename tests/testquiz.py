from flask import url_for
from unittest.mock import patch

from memorizer.models import User
from tests import DatabaseTestCase


def mock_user(registered=False):
        user = User()
        user.registered = registered
        return user


class QuizTest(DatabaseTestCase):
    def test_main(self):
        response = self.client.get('/')
        self.assert200(response)

    @patch('memorizer.views.quiz.get_user', return_value=mock_user())
    def test_register_get(self, mock_get_user):
        response = self.client.get('/register/')
        self.assert_200(response)

    @patch('memorizer.views.quiz.get_user', return_value=mock_user(registered=True))
    def test_register_registered(self, mock_get_user):
        response = self.client.get('/register/')
        self.assert_redirects(response, url_for('quiz.main'))

    @patch('memorizer.views.quiz.get_user', return_value=mock_user())
    def test_register_successful(self, mock_get_user):
        response = self.client.post('/register/', data=self.register_user_data())
        self.assert_redirects(response, url_for('quiz.main'))

    @patch('memorizer.views.quiz.get_user', return_value=mock_user())
    def test_register_fail(self, mock_get_user):
        response = self.client.post('/register/', data=self.register_user_data(username=""))
        self.assert_200(response)

    def register_user_data(self, name='Test User', username='Test', password='password1'):
        return {
            'name': name,
            'username': username,
            'password': password,
            'confirm': password
        }
