from flask.ext.testing import TestCase

from flask import g

from memorizer.application import create_app
from memorizer.database import db
from memorizer.models import User


class MemorizerTestCase(TestCase):
    def create_app(self):
        return create_app('../tests/config.py')


class DatabaseTestCase(MemorizerTestCase):
    def setUp(self):
        super().setUp()
        db.create_all()

    def tearDown(self):
        super().tearDown()
        db.session.remove()
        db.drop_all()

    def set_user(self, user):
        g.user = user

    def mock_user(self, registered=False, save=False):
        user = User()
        user.registered = registered
        user.name = "Name"
        user.username = "name"
        if save:
            db.session.add(user)
            db.session.commit()
        self.set_user(user)
        return user
