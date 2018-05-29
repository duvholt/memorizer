from flask import url_for

from tests import DatabaseTestCase
from tests.models_mock import add_course, add_exam, add_question_boolean, add_question_multiple


class QuestionTest(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.mock_user(save=True)
        self.course = add_course()
        self.exam = add_exam(self.course)
        self.boolean = add_question_boolean(self.exam, text="Test Question", correct=True)
        self.multiple = add_question_multiple(self.exam, text="Test Question", alternatives=[
            ('Alt 1', False),
            ('Alt 2', True),
            ('Alt 3', False),
        ])

    def test_wrong_boolean(self):
        question = self.boolean

        response = self.client.post(url_for('api.answer'), data={'question': question.id, 'correct': 'false'})

        self.assert200(response)
        self.assertFalse(response.json['correct'], 'Answer is not correct')

    def test_correct_boolean(self):
        question = self.boolean

        response = self.client.post(url_for('api.answer'), data={'question': question.id, 'correct': 'true'})

        self.assert200(response)
        self.assertTrue(response.json['correct'], 'Answer is correct')

    def test_correct_multiple(self):
        question = self.multiple

        response = self.client.post(
            url_for('api.answer'),
            data={'question': question.id, 'alternative': question.alternatives[1].id}
        )

        self.assert200(response)
        self.assertTrue(response.json['correct'], 'Answer is correct')

    def test_wrong_multiple(self):
        question = self.multiple

        response = self.client.post(
            url_for('api.answer'),
            data={'question': question.id, 'alternative': question.alternatives[2].id}
        )

        self.assert200(response)
        self.assertFalse(response.json['correct'], 'Answer is incorrect')

    def test_wrong_multiple_several_answers(self):
        question = self.multiple

        response = self.client.post(
            url_for('api.answer'),
            data={'question': question.id, 'alternative': [question.alternatives[0].id, question.alternatives[1].id]}
        )

        self.assert200(response)
        self.assertFalse(response.json['correct'], 'Answer is incorrect')

    def test_correct_multiple_several_answers(self):
        exam = add_exam(self.course, multiple_correct=True)
        question = add_question_multiple(exam, text="Test Question", alternatives=[
            ('Alt 1', True),
            ('Alt 2', True),
            ('Alt 3', False),
        ])

        response = self.client.post(
            url_for('api.answer'),
            data={'question': question.id, 'alternative': [question.alternatives[0].id, question.alternatives[1].id]}
        )

        self.assert200(response)
        self.assertTrue(response.json['correct'], 'Answer is incorrect')

    def test_correct_multiple_one_answer_several_correct(self):
        exam = add_exam(self.course, multiple_correct=False)
        question = add_question_multiple(exam, text="Test Question", alternatives=[
            ('Alt 1', True),
            ('Alt 2', True),
            ('Alt 3', False),
        ])

        response = self.client.post(
            url_for('api.answer'),
            data={'question': question.id, 'alternative': [question.alternatives[1].id]}
        )

        self.assert200(response)
        self.assertTrue(response.json['correct'], 'Answer is correct')
