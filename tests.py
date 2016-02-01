import unittest
from flask.ext.testing import TestCase
from memorizer.application import create_app
from memorizer.database import db
from memorizer import models


class MemorizerTestCase(TestCase):
    SQLALCHEMY_DATABASE_URI = "sqlite://"
    TESTING = True

    def create_app(self):
        return create_app()

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


class SomeTest(MemorizerTestCase):
    def test_something(self):

        user = models.User()
        db.session.add(user)
        db.session.commit()

        # this works
        assert user in db.session

        response = self.client.get("/")

        # this raises an AssertionError
        assert user in db.session


if __name__ == '__main__':
    unittest.main()
