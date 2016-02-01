from flask import url_for
from sqlalchemy import orm
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import FlaskPlugin
from sqlalchemy_utils import force_auto_coercion
from sqlalchemy_utils.types.choice import ChoiceType
from sqlalchemy_utils.types.password import PasswordType
from werkzeug.utils import cached_property

from .database import db
from .utils import fetch_current_user_id, generate_stats

force_auto_coercion()
make_versioned(plugins=[FlaskPlugin(current_user_id_factory=fetch_current_user_id)])


class Course(db.Model):
    __versioned__ = {}
    __tablename__ = 'course'
    __mapper_args__ = {'order_by': 'code'}
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True, nullable=False, info={'label': 'Emnekode'})
    name = db.Column(db.String(120), nullable=False, info={'label': 'Navn'})
    exams = db.relationship('Exam', backref='course')
    questions = association_proxy('exams', 'questions')

    def __init__(self, code=None, name=None):
        self.code = code
        self.name = name

    @cached_property
    def question_count(self):
        return Question.query.filter_by(course=self).count()

    def question(self, id):
        return Question.query.filter_by(course=self).offset(id - 1).limit(1)

    def stats(self):
        return generate_stats(course_code=self.code)

    def __repr__(self):
        return self.code + ' ' + self.name

    def serialize(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'str': str(self)
        }

    @property
    def string(self):
        return self.code


class Exam(db.Model):
    __versioned__ = {}
    __tablename__ = 'exam'
    __mapper_args__ = {'order_by': 'name'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, info={'label': 'Navn'})
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    questions = db.relationship('Question', backref='exam')

    def __init__(self, name=None, course_id=None):
        self.name = name
        self.course_id = course_id

    @cached_property
    def question_count(self):
        return Question.query.filter_by(exam=self).count()

    def question(self, id):
        return Question.query.filter_by(exam=self).offset(id - 1).limit(1)

    def stats(self):
        return generate_stats(course_code=self.course.code, exam_name=self.name)

    def __repr__(self):
        return self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'course_id': self.course_id
        }

    @property
    def string(self):
        return self.course.code + '_' + self.name


class Question(db.Model):
    __versioned__ = {}
    MULTIPLE = '1'
    BOOLEAN = '2'
    TYPES = [
        (MULTIPLE, 'Flervalg'),
        (BOOLEAN, 'Ja/Nei')
    ]
    __tablename__ = 'question'
    __mapper_args__ = {'order_by': 'id'}
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, info={'label': 'Oppgavetekst'})
    image = db.Column(db.String, info={'label': 'Bilde'})
    exam_id = db.Column(db.Integer, db.ForeignKey('exam.id'))
    course = association_proxy('exam', 'course')
    reason = db.Column(db.String, info={'label': 'Forklaring'})

    type = db.Column(ChoiceType(TYPES), info={'label': 'Spørsmålstype'})
    # Boolean question
    correct = db.Column(db.Boolean, info={'label': 'Korrekt'})
    # Alternative question
    alternatives = db.relationship('Alternative', backref='question', order_by='Alternative.id')

    def __init__(self, type=None, text=None, exam_id=None, image="", correct=None):
        self.type = type
        self.text = text
        self.exam_id = exam_id
        self.image = image
        self.correct = correct

    def __repr__(self):
        return self.text

    @property
    def multiple(self):
        return self.type == self.MULTIPLE

    @property
    def choices(self):
        if self.multiple:
            return self.alternatives

    @property
    def index(self):
        return Question.find_index(self)

    @classmethod
    def find_index(cls, question):
        indexes = [q.id for q in cls.query.filter_by(exam_id=question.exam_id).all()]
        return indexes.index(question.id) + 1

    def serialize(self):
        response = {
            'id': self.id,
            'text': self.text,
            'exam_id': self.exam_id,
            'multiple': self.multiple,
            'type': self.type.code
        }
        if self.multiple:
            response['alternatives'] = []
            for alt in self.alternatives:
                alt_dict = alt.serialize()
                del alt_dict['question_id']
                response['alternatives'].append(alt_dict)
        else:
            response['correct'] = self.correct
        if self.image:
            # this is not efficient
            response['image'] = url_for('static', filename='img/' + self.course.code + '/' + self.image)
        return response


class Alternative(db.Model):
    __versioned__ = {}
    __tablename__ = 'alternative'
    __mapper_args__ = {'order_by': 'id'}

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, info={'label': 'Tekst'})
    correct = db.Column(db.Boolean, info={'label': 'Korrekt'})
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))

    def __init__(self, text=None, correct=None, question_id=None):
        self.text = text
        self.correct = correct
        self.question_id = question_id

    def __repr__(self):
        return self.text

    def serialize(self):
        return {
            'id': self.id,
            'text': self.text,
            'correct': self.correct,
            'question_id': self.question_id
        }


class User(db.Model):
    __tablename__ = 'user'
    __mapper_args__ = {'order_by': 'id'}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, info={'label': 'Navn'})
    username = db.Column(db.String, unique=True, info={'label': 'Brukernavn'})
    password = db.Column(PasswordType(schemes=['pbkdf2_sha512']), info={'label': 'Passord'})
    registered = db.Column(db.Boolean)
    admin = db.Column(db.Boolean)

    def __init__(self):
        self.registered = False
        self.admin = False

    def __repr__(self):
        return self.username


class Stats(db.Model):
    __tablename__ = 'stats'
    __mapper_args__ = {'order_by': 'id'}

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    correct = db.Column(db.Boolean)
    reset = db.Column(db.Boolean)

    question = db.relationship('Question', backref='stats')
    user = db.relationship('User', backref='stats')

    def __init__(self, user, question, correct):
        self.user_id = user.id
        self.question_id = question.id
        self.correct = correct
        self.reset = False

    @classmethod
    def course(cls, user, course_code):
        return cls.query.filter_by(reset=False, user_id=user.id).join(Question).join(Exam).join(Course).\
            filter_by(code=course_code)

    @classmethod
    def exam(cls, user, course_code, exam_name):
        return cls.query.filter_by(reset=False, user_id=user.id).join(Question).join(Exam).join(Course).\
            filter(Course.code == course_code).\
            filter(Exam.name == exam_name)

    @classmethod
    def answered(cls, user, question):
        return cls.query.filter_by(user=user, question=question, reset=False).count() > 0

orm.configure_mappers()
