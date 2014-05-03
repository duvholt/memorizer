from main import db


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(80), unique=True)
    name = db.Column(db.String(120))
    questions = db.relationship("Question", backref='course')

    def __init__(self, code, name):
        self.code = code
        self.name = name

    def __repr__(self):
        return self.code + ' ' + self.name


class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    text = db.Column(db.String)
    correct = db.Column(db.Integer)
    alternatives = db.relationship("Alternative", backref='question', order_by='Alternative.number')
    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))

    def __init__(self, number, text, course_id, correct):
        self.number = number
        self.text = text
        self.correct = correct
        self.course_id = course_id

    def __repr__(self):
        return self.text


class Alternative(db.Model):
    __tablename__ = 'alternative'

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    text = db.Column(db.String)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id"))

    def __init__(self, text, number, question_id):
        self.text = text
        self.number = number
        self.question_id = question_id

    def __repr__(self):
        return self.text
