from flask import url_for, session
from unittest.mock import patch
import random

from memorizer.database import db
from memorizer.models import Course, Exam, Question, Stats, User
from memorizer.utils import generate_stats
from tests import DatabaseTestCase, MemorizerTestCase
from tests.models_mock import add_course, add_exam, add_question_multiple


class QuizTest(DatabaseTestCase):
    def test_main(self):
        response = self.client.get('/')
        self.assert200(response)


class QuizRegisterTest(DatabaseTestCase):
    def test_register_get(self):
        self.mock_user()
        response = self.client.get('/register/')
        self.assert_200(response)

    def test_register_registered(self):
        self.mock_user(registered=True)
        response = self.client.get('/register/')
        self.assert_redirects(response, url_for('quiz.main'))

    def test_register_registered_post(self):
        self.mock_user(registered=True)
        response = self.client.post('/register/', data=self.register_user_data())
        self.assert_redirects(response, url_for('quiz.main'))

    def test_register_successful(self):
        user = self.mock_user()

        response = self.client.post('/register/', data=self.register_user_data())
        db_user = User.query.get(user.id)

        self.assertIsNotNone(user.id)
        self.assertTrue(user.registered)
        self.assertTrue(db_user.registered)
        self.assert_redirects(response, url_for('quiz.main'))

    def test_register_empty_username(self):
        user = self.mock_user()

        response = self.client.post('/register/', data=self.register_user_data(username=""))

        self.assertIsNone(user.id)
        self.assert_200(response)

    def test_register_unmatching_passwords(self):
        user = self.mock_user()

        self.client.post(
            '/register/',
            data=self.register_user_data(password="password1", confirm="password2")
        )

        self.assertIsNone(user.id)

    def register_user_data(self, name='Test User', username='Test', password='password1', confirm=None):
        return {
            'name': name,
            'username': username,
            'password': password,
            'confirm': confirm if confirm is not None else password
        }


class QuizLoginTest(DatabaseTestCase):
    def test_login_get(self):
        self.mock_user()
        response = self.client.get('/login/')
        self.assert_200(response)

    def test_login_already_logged_in(self):
        self.mock_user(registered=True)
        response = self.client.get('/login/')
        self.assert_redirects(response, url_for('quiz.main'))

    def test_login_successful(self):
        self.mock_user()
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

    def test_login_fail(self):
        self.mock_user()
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


class QuizLogoutTest(MemorizerTestCase):
    def test_login_logged_in(self):
        with self.client.session_transaction() as sess:
            print(sess.__dict__)
            sess['user'] = 123
        response = self.client.get('/logout/')
        self.assert_redirects(response, url_for('quiz.main'))
        self.assertNotIn('user', session)

    def test_login_logged_out(self):
        response = self.client.get('/logout/')
        self.assert_redirects(response, url_for('quiz.main'))


class RenderViewTest(DatabaseTestCase):
    def test_tips(self):
        response = self.client.get('/tips/')
        self.assert200(response)


class ResetStatsTest(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.user = self.mock_user(save=True)
        db.session.add(self.user)
        db.session.commit()
        # Add 5 courses with 3 exams each with stats
        for course_n in range(5):
            course = Course("TEST%d" % course_n, "Test Course")
            db.session.add(course)
            db.session.commit()
            for exam_n in range(3):
                exam = Exam("V%d" % exam_n, course.id)
                db.session.add(exam)
                db.session.commit()
                question = Question(exam_id=exam.id, type=Question.BOOLEAN, text="Test Question", correct=True)
                db.session.add(question)
                db.session.commit()
                for stats_n in range(2):
                    stats = Stats(self.user, question, random.choice([True, False]))
                    db.session.add(stats)
        db.session.commit()

    def test_reset_exam(self):
        course = Course.query.all()[2]
        exam = course.exams[1]

        stats_query = Stats.exam(self.user, course.code, exam.name).with_entities(Stats.id).subquery()
        stats_count_all = Stats.query.filter_by(reset=False).count()
        stats_count = Stats.query.filter(Stats.id.in_(stats_query)).count()
        self.assertTrue(stats_count > 0)

        response = self.client.get('/reset/{course}/{exam}/'.format(course=course.code, exam=exam.name))
        self.assert_redirects(response, url_for('quiz.exam', course=course.code, exam=exam.name))

        stats_count_all_after = Stats.query.filter_by(reset=False).count()
        stats_count_after = Stats.query.filter(Stats.id.in_(stats_query)).count()
        self.assertTrue(stats_count_after == 0)
        self.assertEqual(stats_count_all_after, stats_count_all - stats_count)

    def test_reset_course(self):
        course = Course.query.all()[1]

        stats_query = Stats.course(self.user, course.code).with_entities(Stats.id).subquery()
        stats_count_all = Stats.query.filter_by(reset=False).count()
        stats_count = Stats.query.filter(Stats.id.in_(stats_query)).count()
        self.assertTrue(stats_count > 0)

        response = self.client.get('/reset/{course}/'.format(course=course.code))
        self.assert_redirects(response, url_for('quiz.course', course=course.code))

        stats_count_all_after = Stats.query.filter_by(reset=False).count()
        stats_count_after = Stats.query.filter(Stats.id.in_(stats_query)).count()
        self.assertTrue(stats_count_after == 0)
        self.assertEqual(stats_count_all_after, stats_count_all - stats_count)


class RedirectTest(DatabaseTestCase):
    @patch('memorizer.views.quiz.utils.random_id', return_value=1)
    def test_course(self, random_patch):
        course = Course(code='TEST1', name='Course')
        db.session.add(course)
        db.session.commit()
        response = self.client.get('/%s/' % course.code)
        self.assert_redirects(
            response, url_for('quiz.question_course', course_code=course.code, id=1)
        )

    @patch('memorizer.views.quiz.utils.random_id', return_value=1)
    def test_exam(self, random_patch):
        course = Course(code='TEST1', name='Course')
        db.session.add(course)
        db.session.commit()

        exam = Exam("H1", course.id)
        db.session.add(exam)
        db.session.commit()

        response = self.client.get('/%s/%s/' % (course.code, exam.name))
        self.assert_redirects(
            response, url_for('quiz.question_exam', course_code=course.code, exam_name=exam.name, id=1)
        )


class QuestionTest(DatabaseTestCase):
    def setUp(self):
        super().setUp()
        self.mock_user(save=True)
        self.course = add_course()
        exam = add_exam(self.course)
        # self.multiple = Question(exam_id=exam.id, type=Question.MULTIPLE, text="Test Question")
        self.boolean = Question(exam_id=exam.id, type=Question.BOOLEAN, text="Test Question", correct=True)
        db.session.add(self.boolean)
        db.session.commit()

    def test_view(self):
        question = self.boolean
        response = self.client.get(url_for('quiz.question_course', course_code=question.course.code, id=1))
        self.assert200(response)

    def test_answer(self):
        question = self.boolean
        stats_data = generate_stats(question.course.code, question.exam.name)
        url = url_for('quiz.question_course', course_code=question.course.code, id=question.id)

        response = self.post_answer(url)
        stats_data_after = generate_stats(question.course.code, question.exam.name)

        self.assertEqual(stats_data['combo'] + 1, stats_data_after['combo'])
        self.assert200(response)

    def test_answer_multiple_correct_one_answer(self):
        exam = add_exam(self.course, name="TEST2", multiple_correct=False)
        question = add_question_multiple(exam, text="Test Question", alternatives=[
            ('Alt 1', True),
            ('Alt 2', True),
            ('Alt 3', False),
        ])
        stats_data = generate_stats(question.course.code, question.exam.name)
        url = url_for('quiz.question_course', course_code=question.course.code, id=question.id)

        response = self.post_answer(url, [question.alternatives[1].id])

        stats_data_after = generate_stats(question.course.code, question.exam.name)
        self.assertEqual(stats_data['combo'] + 1, stats_data_after['combo'])
        self.assert200(response)

    def test_answer_multiple_correct_multiple_answer(self):
        exam = add_exam(self.course, name="TEST2", multiple_correct=True)
        question = add_question_multiple(exam, text="Test Question", alternatives=[
            ('Alt 1', True),
            ('Alt 2', True),
            ('Alt 3', False),
        ])
        stats_data = generate_stats(question.course.code, question.exam.name)
        url = url_for('quiz.question_course', course_code=question.course.code, id=question.id)

        response = self.post_answer(url, [question.alternatives[0].id, question.alternatives[1].id])

        stats_data_after = generate_stats(question.course.code, question.exam.name)
        self.assertEqual(stats_data['combo'] + 1, stats_data_after['combo'])
        self.assert200(response)

    def post_answer(self, url, answer='true'):
        response = self.client.post(url, data={'answer': answer})
        return response
