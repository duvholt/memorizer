from flask_testing import TestCase

from memorizer.application import create_app
from memorizer.database import db


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
