from flask import Flask

from tests import MemorizerTestCase


class ApplicationTest(MemorizerTestCase):
    def test_create_app(self):
        app = self.create_app()
        self.assertIsInstance(app, Flask)
