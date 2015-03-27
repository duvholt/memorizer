from flask import Blueprint, render_template
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form
import models

admin = Blueprint('admin', __name__, template_folder='templates/admin')


def index():
    pass


@admin.route('/courses')
def courses():
    context = dict(courses=models.Course.query.all())
    return render_template('admin/courses.html', **context)


@admin.route('/course/<string:course_code>', methods=['GET', 'POST'])
def course(course_code):
    CourseForm = model_form(models.Course, base_class=Form)
    course = models.Course.query.filter_by(code=course_code).first_or_404()
    form = CourseForm(obj=course)
    context = dict(course=course, form=form)
    return render_template('admin/course.html', **context)


@admin.route('/course/<string:course_code>/<string:exam_name>/', methods=['GET', 'POST'])
def exam(course_code, exam_name):
    ExamForm = model_form(models.Exam, base_class=Form)
    course = models.Course.query.filter_by(code=course_code).first_or_404()
    exam = models.Exam.query.filter_by(course=course, name=exam_name).first_or_404()
    form = ExamForm(obj=exam)
    context = dict(exam=exam, course=course, form=form)
    return render_template('admin/exam.html', **context)


@admin.route('/question/<int:question_id>/', methods=['GET', 'POST'])
def question(question_id=None):
    QuestionForm = model_form(models.Question, base_class=Form)
    if question_id is not None:
        question = question = models.Question.query.filter_by(id=question_id).first_or_404()
    else:
        question = None
    form = QuestionForm(obj=question)
    if form.validate_on_submit():
        print('yolo')
    context = dict(question=question, form=form)
    return render_template('admin/question.html', **context)
