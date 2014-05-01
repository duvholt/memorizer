from .main import app
from flask.ext.sqlalchemy import SQLAlchemy

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


class Course(db.Model):
    __tablename__ = 'course'
    code = db.Column(db.String(80), primary_key=True)
    name = db.Column(db.String(120), unique=True)
    questions = db.relationship("Question", backref='course')

    def __init__(self, code, name):
        self.code = code
        self.name = name

    def __repr__(self):
        return self.name


class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    correct = db.Column(db.Integer)
    alternative = db.relationship("Alternative", backref='question')
    course_id = db.Column(db.Integer, db.ForeignKey("course.code"))

    def __init__(self, text, course_id, correct):
        self.text = text
        self.correct = correct
        self.course_id = course_id

    def __repr__(self):
        return self.text



class Alternative(db.Model):
    __tablename__ = 'alternative'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))

    def __init__(self, text, question):
        self.text = text
        self.question_id = question_id
