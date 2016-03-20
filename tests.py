#!/usr/bin/env python3
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


class ModelTestCase:
    model = None

    def create(self):
        return self.model()

    def edit(self, object):
        raise NotImplementedError

    def test_add(self):
        object = self.create()
        db.session.add(object)
        db.session.commit()

        assert object in db.session
        self.assertIsNotNone(self.model.query.get(object.id))

    def test_edit(self):
        object = self.create()
        db.session.add(object)
        db.session.commit()

        object_copy = self.copy_object(object)

        self.assertTrue(self.equal_keys(object, object_copy))

        self.edit(object)
        db.session.add(object)
        db.session.commit()
        self.assertFalse(self.equal_keys(object, object_copy))

    def copy_object(self, object):
        object_keys = object.__table__.columns.keys()
        object_keys.remove('id')
        return {key: getattr(object, key) for key in object_keys}

    def equal_keys(self, object, object2):
        for key in object2.keys():
            if getattr(object, key) != object2[key]:
                return False
        return True

    def test_delete(self):
        object = self.create()
        db.session.add(object)
        db.session.commit()

        self.assertIsNotNone(self.model.query.get(object.id))
        db.session.delete(object)
        db.session.commit()
        assert object not in db.session
        self.assertIsNone(self.model.query.get(object.id))


class TestUserModel(ModelTestCase, DatabaseTestCase):
    model = models.User

    def edit(self, user):
        user.name = "User"
        user.username = "user"


class TestCourseModel(ModelTestCase, DatabaseTestCase):
    model = models.Course

    def create(self):
        return self.model(code="TEST", name="Test Course")

    def edit(self, course):
        course.code = "TEST2"
        course.name = "Test Course 2"


class TestExamModel(ModelTestCase, DatabaseTestCase):
    model = models.Exam

    def edit(self, exam):
        exam.name = "Exam"


class TestQuestionModel(ModelTestCase, DatabaseTestCase):
    model = models.Question

    def edit(self, question):
        question.text = "Text"


class TestAlternativeModel(ModelTestCase, DatabaseTestCase):
    model = models.Alternative

    def edit(self, alternative):
        alternative.text = "Text"
        alternative.correct = False


class TestStatsModel(ModelTestCase, DatabaseTestCase):
    model = models.Stats

    def create(self):
        MyObject = type('MyObject', (object,), {})
        obj = MyObject()
        obj.id = -1
        return self.model(user=obj, question=obj, correct=False)

    def edit(self, stats):
        stats.correct = True


class CacheTest(MemorizerTestCase):
    pass


if __name__ == '__main__':
    unittest.main()
