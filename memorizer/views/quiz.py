import random

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from memorizer import forms, models, utils
from memorizer.user import get_user
from memorizer.views import TemplateMethodView

quiz = Blueprint('quiz', __name__)


@quiz.route('/')
def main():
    context = {'courses': models.Course.query.all()}
    return render_template('quiz/courses.html', **context)


class Register(TemplateMethodView):
    template = 'quiz/register.html'
    methods = ['GET', 'POST']

    def context(self, *args, **kwargs):
        context = super().context(*args, **kwargs)
        context['form'] = self.form
        return context

    def get(self):
        user = get_user()
        if user.registered:
            flash('Du er allerede logget inn', 'error')
            return redirect(url_for('quiz.main'))
        self.form = forms.RegisterForm()

    def post(self):
        response = self.get()
        if response:
            return response
        form = forms.RegisterForm(request.form)
        if form.validate():
            self.save_user(form)
            flash('Registrering fullført', 'success')
            return redirect(url_for('quiz.main'))
        self.form = form

    def save_user(self, form):
        user = get_user()
        user.name = form.name.data
        user.username = form.username.data
        user.password = form.password.data
        user.registered = True
        models.db.session.add(user)
        models.db.session.commit()


quiz.add_url_rule('/register/', view_func=Register.as_view('register'))


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
    models.Stats.query.filter(models.Stats.id.in_(stats_query)).\
        update({models.Stats.reset: True}, synchronize_session=False)
    models.db.session.commit()
    return redirect(url_for('quiz.course', course=course.code))


@quiz.route('/reset/<string:course>/<string:exam>/')
def reset_stats_exam(course, exam):
    """Reset stats for a course"""
    course = models.Course.query.filter_by(code=course).first_or_404()
    exam = models.Exam.query.filter_by(course=course, name=exam).first_or_404()
    stats_query = models.Stats.exam(get_user(), course.code, exam.name).with_entities(models.Stats.id).subquery()
    models.Stats.query.filter(models.Stats.id.in_(stats_query)).\
        update({models.Stats.reset: True}, synchronize_session=False)
    models.db.session.commit()
    return redirect(url_for('quiz.exam', course=course.code, exam=exam.name))


@quiz.route('/<string:course>/')
@quiz.route('/<string:course>/all/0')
def course(course):
    """Redirects to a random question for a chosen course"""
    models.Course.query.filter_by(code=course).first_or_404()
    return redirect(url_for(
        'quiz.question_course', course_code=course, id=utils.random_id(course=course))
    )


@quiz.route('/<string:course>/<string:exam>/')
@quiz.route('/<string:course>/<string:exam>/0')
def exam(course, exam):
    """Redirects to the first question for a chosen exam"""
    course_m = models.Course.query.filter_by(code=course).first_or_404()
    exam_m = models.Exam.query.filter_by(course=course_m, name=exam).first_or_404()
    return redirect(url_for('quiz.question_exam', course_code=course, exam_name=exam_m.name, id=1))


class QuestionMixin:
    template = 'quiz/question.html'
    methods = ['GET', 'POST']

    def context(self, *args, **kwargs):
        context = super().context(*args, **kwargs)
        context.update({
            'id': self.number,
            'prev': self.next(),
            'next': self.previous(),
            'question': self.question,
            'answered': getattr(self, 'answered', None),
            'success': getattr(self, 'success', None),
            'stats': self.model.stats()
        })
        return context

    def next(self):
        if self.number > 1:
            return self.number - 1
        else:
            return self.model.question_count

    def previous(self):
        if self.number < self.model.question_count:
            return self.number + 1
        else:
            return 1

    def get(self, number, *args, **kwargs):
        if self.model.question_count == 0:
            abort(404)
        self.number = number
        self.question = self.model.question(number).first_or_404()
        self.sort_exams()
        self.scramble_alternatives()

    def post(self, *args, **kwargs):
        self.get(*args, **kwargs)
        answer = request.form.get('answer')
        if answer:
            self.answered = True
            if self.question.multiple:
                self.success = self.alternatives_correct()
            else:
                bool_answer = answer.lower() == 'true'
                self.success = self.question.correct == bool_answer
            user = get_user()
            # Checking if question has already been answered
            if not models.Stats.answered(user, self.question):
                self.save_answer(user, self.success)
            elif self.success:
                flash('Du har allerede svart på dette spørsmålet så du får ikke noe poeng. :-)', 'info')
        else:
            flash('Blankt svar', 'error')
        # Preserving order on submit
        ordering = request.form.get('order')
        if ordering:
            self.reorder_alternatives(ordering)

    def sort_exams(self):
        self.question.course.exams.sort(key=utils.sort_exam, reverse=True)

    def scramble_alternatives(self):
        dict_alt = {alt.id: alt for alt in self.question.alternatives}
        indexes = list(dict_alt.keys())
        random.shuffle(indexes)
        self.question.alternatives = [dict_alt[index] for index in indexes]

    def reorder_alternatives(self, ordering):
        dict_alt = {alt.id: alt for alt in self.question.alternatives}
        indexes = map(int, ordering.split(','))
        self.question.alternatives = [dict_alt[index] for index in indexes]

    def alternatives_correct(self):
        try:
            answers = set(map(int, request.form.getlist('answer')))
        except ValueError:
            return False
        correct_alternatives = models.Alternative.query.filter_by(question=self.question, correct=True)
        correct_answers = {alt.id for alt in correct_alternatives}
        return correct_answers == answers

    def save_answer(self, user, success):
        stat = models.Stats(user, self.question, success)
        models.db.session.add(stat)
        models.db.session.commit()


class CourseQuestion(QuestionMixin, TemplateMethodView):
    def get(self, course_code, id, *args, **kwargs):
        self.model = models.Course.query.filter_by(code=course_code).first_or_404()
        return super().get(id, course_code, *args, **kwargs)

    def context(self, *args, **kwargs):
        context = super().context(*args, **kwargs)
        reset_url = url_for('quiz.reset_stats_course', course=self.model.code)
        random_question = utils.random_id(id=id, course=self.model.code)

        context.update({
            'exam_name': 'all',
            'reset_url': reset_url,
            'random': random_question
        })
        return context


quiz.add_url_rule(
    '/<string:course_code>/all/<int:id>',
    view_func=CourseQuestion.as_view('question_course')
)


class ExamQuestion(QuestionMixin, TemplateMethodView):
    def get(self, course_code, exam_name, id, *args, **kwargs):
        course = models.Course.query.filter_by(code=course_code).first_or_404()
        self.model = models.Exam.query.filter_by(course=course, name=exam_name, hidden=False).first_or_404()
        return super().get(id, course_code, exam_name, *args, **kwargs)

    def context(self, *args, **kwargs):
        context = super().context(*args, **kwargs)
        random_question = utils.random_id(id=id, course=self.model.course.code)
        reset_url = url_for('quiz.reset_stats_exam', course=self.model.course.code, exam=self.model.name)

        context.update({
            'exam_name': self.model.name,
            'reset_url': reset_url,
            'random': random_question
        })
        return context


quiz.add_url_rule(
    '/<string:course_code>/<string:exam_name>/<int:id>',
    view_func=ExamQuestion.as_view('question_exam')
)
