from flask import Blueprint, render_template
from memorizer.forms import CourseForm, ExamForm, QuestionForm, AlternativeForm
from memorizer import models
from memorizer.user import login_required


admin = Blueprint('admin', __name__)


@admin.route('/', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('admin/admin.html')


@admin.route('/courses')
@login_required
def courses():
    context = dict(courses=models.Course.query.all())
    form = CourseForm()
    context['form'] = form
    return render_template('admin/courses.html', **context)


@admin.route('/course/<string:course_id>', methods=['GET', 'POST'])
@login_required
def course(course_id):
    course = models.Course.query.filter_by(id=course_id).first_or_404()
    form = CourseForm(obj=course)
    exam = models.Exam(course_id=course.id)
    exam_form = ExamForm(obj=exam)
    context = dict(course=course, form=form, exam_form=exam_form)
    return render_template('admin/course.html', **context)


@admin.route('/course/<string:course_id>/<string:exam_id>', methods=['GET', 'POST'])
@login_required
def exam(course_id, exam_id):
    course = models.Course.query.filter_by(id=course_id).first_or_404()
    exam = models.Exam.query.filter_by(course=course, id=exam_id).first_or_404()
    form = ExamForm(obj=exam)
    question = models.Question(exam_id=exam.id)
    question_form = QuestionForm(obj=question)
    context = dict(exam=exam, course=course, form=form, question_form=question_form)
    return render_template('admin/exam.html', **context)


@admin.route('/question/<int:question_id>', methods=['GET', 'POST'])
@login_required
def question(question_id):
    question = question = models.Question.query.filter_by(id=question_id).first_or_404()
    query = models.Question.query.filter_by(exam=question.exam)
    prev_question = query.filter(models.Question.id < question_id).order_by('-id').first()
    next_question = query.filter(models.Question.id > question_id).first()
    form = QuestionForm(obj=question)
    alt = models.Alternative(question_id=question.id)
    alt_form = AlternativeForm(obj=alt)
    context = dict(
        question=question, form=form, alt_form=alt_form,
        next_question=next_question, prev_question=prev_question
    )
    return render_template('admin/question.html', **context)


@admin.route('/question/<int:question_id>/<int:alternative_id>')
@login_required
def alternative(question_id, alternative_id):
    question = models.Question.query.filter_by(id=question_id).first_or_404()
    alternative = models.Alternative.query.filter_by(id=alternative_id).first_or_404()
    form = AlternativeForm(obj=alternative)
    context = dict(form=form, question=question, alternative=alternative)
    return render_template('admin/alternative.html', **context)
