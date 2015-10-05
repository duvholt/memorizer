from flask import Blueprint, current_app, flash, g, redirect, request, render_template, session, url_for
from functools import wraps
from forms import CourseForm, ExamForm, QuestionForm, AlternativeForm, LoginForm
from models import db
import models

admin = Blueprint('admin', __name__)


# Decorators
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('admin') is not True:
            return redirect(url_for('admin.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if(request.form.get('password') == current_app.config['ADMIN_PASSWORD']):
            session['admin'] = True
    context = dict(admin=session.get('admin'), form=LoginForm())
    return render_template('admin/admin.html', **context)


@admin.route('/courses')
@admin_required
def courses():
    context = dict(courses=models.Course.query.all())
    form = CourseForm()
    context['form'] = form
    return render_template('admin/courses.html', **context)


@admin.route('/course/<string:course_id>', methods=['GET', 'POST'])
@admin_required
def course(course_id):
    course = models.Course.query.filter_by(id=course_id).first_or_404()
    form = CourseForm(obj=course)
    exam = models.Exam(course_id=course.id)
    exam_form = ExamForm(obj=exam)
    context = dict(course=course, form=form, exam_form=exam_form)
    return render_template('admin/course.html', **context)


@admin.route('/course/<string:course_id>/<string:exam_id>/', methods=['GET', 'POST'])
@admin_required
def exam(course_id, exam_id):
    course = models.Course.query.filter_by(id=course_id).first_or_404()
    exam = models.Exam.query.filter_by(course=course, id=exam_id).first_or_404()
    form = ExamForm(obj=exam)
    question = models.Question(exam_id=exam.id)
    question_form = QuestionForm(obj=question)
    context = dict(exam=exam, course=course, form=form, question_form=question_form)
    return render_template('admin/exam.html', **context)


@admin.route('/question/<int:question_id>/', methods=['GET', 'POST'])
@admin_required
def question(question_id):
    question = question = models.Question.query.filter_by(id=question_id).first_or_404()
    next_question = models.Question.query.filter_by(exam=question.exam).filter(models.Question.id > question_id).first()
    form = QuestionForm(obj=question)
    alt = models.Alternative(question_id=question.id)
    alt_form = AlternativeForm(obj=alt)
    context = dict(question=question, form=form, alt_form=alt_form, next_question=next_question)
    return render_template('admin/question.html', **context)


@admin.route('/question/<int:question_id>/<int:alternative_id>')
@admin_required
def alternative(question_id, alternative_id):
    question = models.Question.query.filter_by(id=question_id).first_or_404()
    alternative = models.Alternative.query.filter_by(id=alternative_id).first_or_404()
    form = AlternativeForm(obj=alternative)
    context = dict(form=form, question=question, alternative=alternative)
    return render_template('admin/alternative.html', **context)
