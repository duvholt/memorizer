from flask import url_for
from unittest.mock import patch

from memorizer.database import db
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


class QuizRegisterTest(DatabaseTestCase):
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


class QuizLoginTest(DatabaseTestCase):
    @patch('memorizer.views.quiz.get_user', return_value=mock_user())
    def test_login_get(self, mock_get_user):
        response = self.client.get('/login/')
        self.assert_200(response)

    @patch('memorizer.views.quiz.get_user', return_value=mock_user(registered=True))
    def test_login_already_logged_in(self, mock_get_user):
        response = self.client.get('/login/')
        self.assert_redirects(response, url_for('quiz.main'))

    @patch('memorizer.views.quiz.get_user', return_value=mock_user())
    def test_login_successful(self, mock_get_user):
        username = 'Test1'
        password = 'password2'
        user = User()
        user.username = username
        user.password = password
        user.registered = True
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login/', data=self.login_user_data(username, password))
        self.assert_redirects(response, url_for('quiz.main'))

    @patch('memorizer.views.quiz.get_user', return_value=mock_user())
    def test_login_fail(self, mock_get_user):
        username = 'username1'
        password = 'pass1'
        user = User()
        user.username = username
        user.password = password
        user.registered = True
        db.session.add(user)
        db.session.commit()

        response = self.client.post('/login/', data=self.login_user_data(username, 'pass2'))
        self.assert_200(response)

    def login_user_data(self, username='Test', password='password1'):
        return {
            'username': username,
            'password': password
        }
