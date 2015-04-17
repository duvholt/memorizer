from flask import Blueprint, flash, g, redirect, request, render_template
from functools import wraps
from forms import CourseForm, ExamForm, QuestionForm
from models import db
import models

admin = Blueprint('admin', __name__)


def index():
    pass


@admin.route('/courses')
def courses():
    context = dict(courses=models.Course.query.all())
    form = CourseForm()
    context['form'] = form
    return render_template('admin/courses.html', **context)


@admin.route('/course/<string:course_code>', methods=['GET', 'POST'])
def course(course_code):
    course = models.Course.query.filter_by(code=course_code).first_or_404()
    form = CourseForm(obj=course)
    if form.validate_on_submit():
        form.populate_obj(course)
        db.session.commit()
        flash('Emne ble lagret')
    else:
        flash('Emne ble ikke lagret')  # Why?
    context = dict(course=course, form=form)
    return render_template('admin/course.html', **context)


@admin.route('/course/<string:course_code>/<string:exam_name>/', methods=['GET', 'POST'])
def exam(course_code, exam_name):
    course = models.Course.query.filter_by(code=course_code).first_or_404()
    exam = models.Exam.query.filter_by(course=course, name=exam_name).first_or_404()
    form = ExamForm(obj=exam)
    if form.validate_on_submit():
        form.populate_obj(exam)
        db.session.commit()
        flash('Eksamen ble lagret')
    else:
        flash('Eksamen ble ikke lagret')  # Why?
    context = dict(exam=exam, course=course, form=form)
    return render_template('admin/exam.html', **context)


@admin.route('/question/<int:question_id>/', methods=['GET', 'POST'])
def question(question_id):
    question = question = models.Question.query.filter_by(id=question_id).first_or_404()
    form = QuestionForm(obj=question)
    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.commit()
        flash('Spørsmål ble lagret')
    else:
        flash('Spørsmål ble ikke lagret')  # Why?
    context = dict(question=question, form=form)
    return render_template('admin/question.html', **context)


# Decorators

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TO DO: Implement admin logic
        return f(*args, **kwargs)
