from unittest import TestCase
from unittest.mock import patch

from memorizer import importer


class ValidateQuestions(TestCase):
    def test_empty(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_questions({})

        with self.assertRaises(importer.ValidationError):
            importer.validate_questions({'key': 'value'})

    def test_not_list(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_questions({'questions': 'value'})

    def test_empty_list(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_questions({'questions': []})

    @patch('memorizer.importer.validate_question', side_effect=importer.ValidationError)
    def test_invalid_question(self, test_patch):
        with self.assertRaises(importer.ValidationError):
            importer.validate_questions({'questions': [{'question': 'test'}]})

    @patch('memorizer.importer.validate_question')
    def test_valid(self, test_patch):
        # Check to see that exception are raised
        importer.validate_questions({'questions': [{'something': 1}]})


class ValidateQuestion(TestCase):
    def test_empty(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({})

    def test_invalid(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'key': 'value'})

    def test_invalid_type(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 1})

    def test_empty_string(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': ''})

    def test_missing_answer(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value'})

    def test_answers_invalid_type(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value', 'answers': 1})

    def test_answers_too_few_answers(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value', 'answers': [1]})

    def test_answers_missing_correct(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value', 'answers': ["1", "2"]})

    def test_answers_correct_wrong_type(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value', 'answers': ["1", "2"], 'correct': None})

    def test_answers_correct_empty(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value', 'answers': ["1", "2"], 'correct': []})

    def test_alternatives_wrong_type(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value', 'answers': [1, "2"], 'correct': 1})

    def test_alternatives_empty(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value', 'answers': ["1", ""], 'correct': 1})

    def test_correct_answers_type(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value', 'answers': ["1", "2"], 'correct': [None]})

    def test_correct_answers_out_of_bounds(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value', 'answers': ["1", "2"], 'correct': 3})
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value', 'answers': ["1", "2"], 'correct': -1})

    def test_boolean_wrong_type(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_question({'question': 'value', 'answer': None})

    def test_valid(self):
        importer.validate_question({'question': 'value', 'answer': True})
        importer.validate_question({'question': 'value', 'answer': False})
        importer.validate_question({'question': 'value', 'answers': ["1", "2"], 'correct': 0})
        importer.validate_question({'question': 'value', 'answers': ["1", "2"], 'correct': 1})
        importer.validate_question({'question': 'value', 'answers': ["1", "2", "3"], 'correct': 1})
        importer.validate_question({'question': 'value', 'answers': ["1", "2", "3"], 'correct': 1})


class ValidateExam(TestCase):
    def test_empty(self):
        with self.assertRaises(importer.ValidationError):
            importer.validate_exam({})

    @patch('memorizer.importer.validate_questions')
    def test_code(self, test_patch):
        with self.assertRaises(importer.ValidationError):
            importer.validate_exam({'key': 'value', 'name': 'Name', 'exam': 'Exam'})

        with self.assertRaises(importer.ValidationError):
            importer.validate_exam({'code': 1, 'name': 'Name', 'exam': 'Exam'})

        with self.assertRaises(importer.ValidationError):
            importer.validate_exam({'code': None, 'name': 'Name', 'exam': 'Exam'})

        with self.assertRaises(importer.ValidationError):
            importer.validate_exam({'code': '', 'name': 'Name', 'exam': 'Exam'})

        importer.validate_exam({'code': 'Code', 'name': 'Name', 'exam': 'Exam'})

    @patch('memorizer.importer.validate_questions')
    def test_name(self, test_patch):
        with self.assertRaises(importer.ValidationError):
            importer.validate_exam({'code': 'Code', 'exam': 'Exam'})

        with self.assertRaises(importer.ValidationError):
            importer.validate_exam({'code': 'Code', 'name': None, 'exam': 'Exam'})

        with self.assertRaises(importer.ValidationError):
            importer.validate_exam({'code': 'Code', 'name': '', 'exam': 'Exam'})

        importer.validate_exam({'code': 'code', 'name': 'Name', 'exam': 'Exam'})

    @patch('memorizer.importer.validate_questions')
    def test_exam(self, test_patch):
        with self.assertRaises(importer.ValidationError):
            importer.validate_exam({'code': 'code', 'name': 'Name'})

        with self.assertRaises(importer.ValidationError):
            importer.validate_exam({'code': 'code', 'name': 'Name', 'exam': None})

        with self.assertRaises(importer.ValidationError):
            importer.validate_exam({'code': 'code', 'name': 'Name', 'exam': ''})

        importer.validate_exam({'code': 'code', 'name': 'Name', 'exam': 'Exam'})
