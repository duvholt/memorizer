from tests import DatabaseTestCase


class QuizTest(DatabaseTestCase):
    def test_main(self):
        response = self.client.get('/')
        self.assert200(response)
