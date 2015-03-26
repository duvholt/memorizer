from flask import render_template
import models


def index():
    pass


# Courses

def courses():
    context = dict(courses=models.Course.query.all())
    return render_template('admin/courses.html', **context)


def course(course_code):
    course = models.Course.query.filter_by(code=course_code).first_or_404()
    context = dict(course=course)
    return render_template('admin/course.html', **context)


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
