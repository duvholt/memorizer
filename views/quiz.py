from flask import abort, Blueprint, flash, redirect, render_template, request, session, url_for
import forms
import models
import random
from user import get_user
import utils

quiz = Blueprint('quiz', __name__)


@quiz.route('/')
def main():
    courses = models.Course.query.all()
    for course in courses:
        course.num_questions = models.Question.query.filter_by(course=course).count()
    context = {
        'courses': courses
    }
    return render_template('quiz/courses.html', **context)


@quiz.route('/register/', methods=['GET', 'POST'])
def register():
    user = get_user()
    if user.registered:
        flash('Du er allerede logget inn', 'error')
        return redirect(url_for('quiz.main'))
    if request.method == 'POST':
        form = forms.RegisterForm(request.form)
        if form.validate():
            user.name = form.name.data
            user.username = form.username.data
            user.password = form.password.data
            user.registered = True
            models.db.session.add(user)
            models.db.session.commit()
            flash('Registrering fullført', 'success')
            return redirect(url_for('quiz.main'))
    else:
        form = forms.RegisterForm()
    context = dict(form=form)
    return render_template('quiz/register.html', **context)

@quiz.route('/login/', methods=['GET', 'POST'])
def login():
    user = get_user()
    if user.registered:
        flash('Du er allerede logget inn', 'error')
        return redirect(url_for('quiz.main'))
    if request.method == 'POST':
        form = forms.LoginForm(request.form)
        if form.validate():
            # Login
            user = models.User.query.filter_by(username=form.username.data).first()
            if user and user.password == form.password.data:
                session['user'] = user.id
                return redirect(url_for('quiz.main'))
    else:
        form = forms.LoginForm()
    context = dict(form=form)
    return render_template('quiz/login.html', **context)

@quiz.route('/logout/')
def logout():
    if 'user' in session:
        del session['user']
    return redirect(url_for('quiz.main'))

@quiz.route('/tips/')
def tips():
    return render_template('quiz/tips.html')


@quiz.route('/reset/<string:course>/')
def reset_stats_course(course):
    """Reset stats for a course"""
    # Check if course exists
    course = models.Course.query.filter_by(code=course).first_or_404()
    stats_query = models.Stats.course(get_user(), course.code).with_entities(models.Stats.id).subquery()
    models.Stats.query.filter(models.Stats.id.in_(stats_query)).update({models.Stats.reset: True}, synchronize_session=False)
    models.db.session.commit()
    return redirect(url_for('quiz.course', course=course.code))


@quiz.route('/reset/<string:course>/<string:exam>/')
def reset_stats_exam(course, exam):
    """Reset stats for a course"""
    course = models.Course.query.filter_by(code=course).first_or_404()
    exam = models.Exam.query.filter_by(course=course, name=exam).first_or_404()
    stats_query = models.Stats.exam(get_user(), course.code, exam.name).with_entities(models.Stats.id).subquery()
    models.Stats.query.filter(models.Stats.id.in_(stats_query)).update({models.Stats.reset: True}, synchronize_session=False)
    models.db.session.commit()
    return redirect(url_for('quiz.exam', course=course.code, exam=exam.name))


@quiz.route('/<string:course>/')
def course(course):
    """Redirects to a random question for a chosen course"""
    course_m = models.Course.query.filter_by(code=course).first_or_404()
    return redirect(url_for('quiz.show_question', course=course, exam='all', id=utils.random_id(course=course_m)))


@quiz.route('/<string:course>/<string:exam>/')
def exam(course, exam):
    """Redirects to the first question for a chosen exam"""
    course_m = models.Course.query.filter_by(code=course).first_or_404()
    exam_m = models.Exam.query.filter_by(course=course_m, name=exam).first_or_404()
    return redirect(url_for('quiz.show_question', course=course, exam=exam_m.name, id=1))


@quiz.route('/<string:course>/<string:exam>/<int:id>', methods=['GET', 'POST'])
def show_question(course, exam, id):
    if id == 0:
        return redirect(url_for('quiz.show_question', course=course, exam=exam, id=1))
    # Setting default value for session variables
    course = models.Course.query.filter_by(code=course).first_or_404()
    exam_name = exam
    exam = None
    if exam_name != 'all':
        exam = models.Exam.query.filter_by(course=course, name=exam_name).first_or_404()
        # Only question from a specific exam
        num_questions = models.Question.query.filter_by(exam=exam).count()
        question = models.Question.query.filter_by(exam=exam).offset(id - 1).limit(1).first_or_404()
        reset_url = url_for('quiz.reset_stats_exam', course=course.code, exam=exam.name)
    else:
        # All questions
        num_questions = models.Question.query.filter_by(course=course).count()
        question = models.Question.query.filter_by(course=course).offset(id - 1).limit(1).first_or_404()
        reset_url = url_for('quiz.reset_stats_course', course=course.code)
    if num_questions == 0:
        abort(404)
    course.exams.sort(key=utils.sort_exam, reverse=True)
    context = {
        'id': id,
        'random': utils.random_id(id=id, course=course, exam=exam),
        'prev': id - 1 if id > 1 else num_questions,
        'next': id + 1 if id < num_questions else 1,
        'num_questions': num_questions,
        'question': question,
        'exam_name': exam_name,
        'reset_url': reset_url
    }
    # POST request when answering
    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer:
            context['answered'] = True
            if question.multiple:
                try:
                    answer_alt = set(map(int, request.form.getlist('answer')))
                except ValueError:
                    pass
                correct_alt = {alt.id for alt in models.Alternative.query.filter_by(question=question, correct=True)}
                context['success'] = correct_alt == answer_alt
            else:
                bool_answer = answer.lower() == 'true'
                context['success'] = question.correct == bool_answer
            user = get_user()
            # Checking if question has already been answered
            if not models.Stats.answered(user, question):
                stat = models.Stats(user, question, context['success'])
                models.db.session.add(stat)
                models.db.session.commit()
            elif context['success']:
                flash('Du har allerede svart på dette spørsmålet så du får ikke noe poeng. :-)', 'info')
        else:
            flash('Blankt svar', 'error')
        # Preserving order on submit
        ordering = request.form.get('order')
        if ordering:
            # Resorting answers from specific values. Answer is a tuple with id and texts
            # Creating dictionary with id as key
            dict_alt = {alt.id: alt for alt in question.alternatives}
            question.alternatives = [dict_alt[int(x)] for x in ordering.split(',')]
    else:
        # Random order on questions
        random.shuffle(question.alternatives)
    # generate_stats doesn't support 'all' and expects None
    if exam_name == 'all':
        exam_name = None
    context['stats'] = utils.generate_stats(course.code, exam_name)
    return render_template('quiz/question.html', **context)
