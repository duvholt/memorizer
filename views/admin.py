from flask import render_template
import models


def index():
    pass


# Courses

def courses():
    context = dict(courses=models.Course.query.all())
    return render_template('admin/courses.html', **context)


def course(course_id):
    pass


# Exams

def exams():
    pass


def exam(exam_id):
    pass


# Questions

def questions():
    pass


def question(question_id):
    pass
