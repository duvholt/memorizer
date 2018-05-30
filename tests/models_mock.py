from memorizer.models import Course, Exam, Question, Alternative
from memorizer.database import db


def add_exam(course, name="T16", **kwargs):
    exam = Exam(name, course.id, **kwargs)
    db.session.add(exam)
    db.session.commit()
    return exam


def add_course(code="TEST", name="Test Course", **kwargs):
    course = Course(code, name, **kwargs)
    db.session.add(course)
    db.session.commit()
    return course


def add_question(exam, **kwargs):
    question = Question(exam_id=exam.id, **kwargs)
    db.session.add(question)
    db.session.commit()
    return question


def add_question_boolean(exam, text, correct=True, **kwargs):
    return add_question(exam, type=Question.BOOLEAN, text=text, correct=correct, **kwargs)


def add_question_multiple(exam, text, alternatives, **kwargs):
    question = add_question(exam, type=Question.MULTIPLE, text=text, **kwargs)
    for text, correct in alternatives:
        alternative = Alternative(text, correct, question.id)
        db.session.add(alternative)
        db.session.commit()
    return question
