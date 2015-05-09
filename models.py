from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_utils.types.choice import ChoiceType

db = SQLAlchemy()


class Course(db.Model):
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
    __tablename__ = 'exam'
    __mapper_args__ = {'order_by': 'name'}
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, info={'label': 'Navn'})
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    questions = db.relationship('Question', backref='exam')

    def __init__(self, name=None, course_id=None):
        self.name = name
        self.course_id = course_id

    def __repr__(self):
        return self.name

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'course_id': self.course_id,
            'str': str(self)
        }

    @property
    def string(self):
        return self.course.code + '_' + self.name


class FakeAlternative(object):
    def __init__(self, id, text, correct):
        self.id = id
        self.text = text
        self.correct = correct

    def __str__(self):
        return self.text


class Question(db.Model):
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
    def is_multiple(self):
        return self.type == self.MULTIPLE

    @property
    def choices(self):
        """Dynamic choices"""
        if self.is_multiple:
            return self.alternatives
        else:
            # oh gee
            return [FakeAlternative(1, 'Riktig', self.correct is True), FakeAlternative(2, 'Galt', self.correct is False)]

    def serialize(self):
        return {
            'id': self.id,
            'text': self.text,
            'image': self.image,
            'exam_id': self.exam_id,
            'alternatives': [alt.serialize() for alt in self.alternatives],
            'str': str(self)
        }


class Alternative(db.Model):
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
            'question_id': self.question_id,
            'str': str(self)
        }
