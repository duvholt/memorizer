from flask.ext.testing import TestCase

from memorizer.application import create_app


class MemorizerTestCase(TestCase):
    TESTING = True

    def create_app(self):
        return create_app()
