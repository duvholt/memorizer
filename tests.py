import unittest
from flask.ext.testing import TestCase
from flask import Flask
from memorizer.application import create_app
from memorizer.database import db
from memorizer import models


class MemorizerTestCase(TestCase):
    TESTING = True

    def create_app(self):
        return create_app()


class DatabaseTestCase(MemorizerTestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"

    def setUp(self):
        super().setUp()
        db.create_all()

    def tearDown(self):
        super().tearDown()
        db.session.remove()
        db.drop_all()


class ApplicationTest(MemorizerTestCase):
    def test_create_app(self):
        app = create_app()
        self.assertIsInstance(app, Flask)


class TestUserModel(DatabaseTestCase):
    def test_add(self):

        user = models.User()
        db.session.add(user)
        db.session.commit()

        # this works
        assert user in db.session

        self.client.get("/")

        # this raises an AssertionError
        assert user in db.session


class CacheTest(MemorizerTestCase):
    pass


if __name__ == '__main__':
    unittest.main()
