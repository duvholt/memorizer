#!/usr/bin/env python3
from flask import abort, Flask, redirect, render_template, request, session, url_for
from flask.ext.assets import Environment, Bundle
from logging.handlers import SMTPHandler
from models import db
from werkzeug.contrib.fixers import ProxyFix
import logging
import models
import os
import random
import re

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.wsgi_app = ProxyFix(app.wsgi_app)
db.init_app(app)

assets = Environment(app)
js = Bundle('js/app.js', filters='jsmin', output='js/min.%(version)s.js')
css = Bundle('css/font-awesome.min.css', 'css/styles.css', filters='cssmin', output='css/min.%(version)s.css')
assets.register('js', js)
assets.register('css', css)

ADMINS = ['memorizer@cxhristian.com']
if not app.debug:
    mail_handler = SMTPHandler('127.0.0.1',
                               'server-error@cxhristian.com',
                               ADMINS, '[Flask] Memorizer ERROR')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)


@app.route('/')
def main():
    context = {
        'courses': models.Course.query.all()
    }
    return render_template('courses.html', **context)


@app.route('/tips/')
def tips():
    return render_template('tips.html')


@app.route('/reset/<string:course>/')
def reset_stats_course(course):
    """Reset stats for a course"""
    if 'courses' in session:
        course = models.Course.query.filter_by(code=course).first()
        if course and course.string in session['courses']:
            del session['courses'][course.string]
    return redirect(url_for('course', course=course.code))


@app.route('/reset/<string:course>/<string:exam>/')
def reset_stats_exam(course, exam):
    """Reset stats for a course"""
    if 'exams' in session:
        if exam and course + '_' + exam in session['exams']:
            del session['exams'][course + '_' + exam]
    return redirect(url_for('exam', course=course, exam=exam))


@app.route('/<string:course>/')
def course(course):
    """Redirects to a random question for a chosen course"""
    course_m = models.Course.query.filter_by(code=course).first_or_404()
    return redirect(url_for('show_question', course=course, exam='all', id=random_id(course=course_m)))


@app.route('/<string:course>/<string:exam>/')
def exam(course, exam):
    """Redirects to the first question for a chosen exam"""
    course_m = models.Course.query.filter_by(code=course).first_or_404()
    exam_m = models.Exam.query.filter_by(course=course_m, name=exam).first_or_404()
    return redirect(url_for('show_question', course=course, exam=exam_m.name, id=1))


@app.route('/<string:course>/<string:exam>/<int:id>', methods=['GET', 'POST'])
def show_question(course, exam, id):
    if id == 0:
        return redirect(url_for('show_question', course=course, exam=exam, id=1))
    # Setting default value for session variables
    course = models.Course.query.filter_by(code=course).first_or_404()
    exam_name = exam
    exam = None
    if exam_name != 'all':
        exam = models.Exam.query.filter_by(course=course, name=exam_name).first_or_404()
        # Shortened variable
        c_session = session_data(session, 'exams', exam)
        # Only question from a specific exam
        num_questions = models.Question.query.filter_by(exam=exam).count()
        question = models.Question.query.filter_by(exam=exam).offset(id - 1).limit(1).first_or_404()
        reset_url = url_for('reset_stats_exam', course=course.code, exam=exam.name)
    else:
        # Shortened variable
        c_session = session_data(session, 'courses', course)
        # All questions
        num_questions = models.Question.query.filter_by(course=course).count()
        question = models.Question.query.filter_by(course=course).offset(id - 1).limit(1).first_or_404()
        reset_url = url_for('reset_stats_course', course=course.code)
    if num_questions == 0:
        abort(404)
    course.exams.sort(key=sort_exam, reverse=True)
    context = {
        'id': id,
        'alerts': [],
        'random': random_id(id=id, course=course, exam=exam),
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
            for alternative in question.alternatives:
                if str(alternative.number) == answer:
                    context['success'] = alternative.correct
                    break
            # Checking if question has already been answered
            if id not in c_session['answered']:
                c_session['points'] += int(context['success'])
                c_session['total'] += 1
                c_session['answered'].append(id)
                if context['success']:
                    c_session['combo'] += 1
                else:
                    c_session['combo'] = 0
            elif context['success']:
                context['alerts'].append({
                    'msg': 'Du har allerede svart på dette spørsmålet så du får ikke noe poeng. :-)',
                    'level': 'info'
                })
        else:
            context['alerts'].append({'msg': 'Blankt svar', 'level': 'danger'})
        # Preserving order on submit
        ordering = request.form.get('order')
        if ordering:
            # Resorting answers from specific values. Answer is a tuple with id and texts
            question.alternatives = [question.alternatives[int(x)] for x in ordering.split(',')]
    else:
        # Random order on questions
        random.shuffle(question.alternatives)
    context['score'] = c_session
    return render_template('question.html', **context)


def random_id(id=None, course=None, exam=None):
    """
        Returns a random id from questions that have not been answered.
        Returns a random number if none available
    """
    if exam:
        num_questions = models.Question.query.filter_by(exam=exam).count()
        answered = session.get('exams', {}).get(exam.string, {}).get('answered', [])
    elif course:
        num_questions = models.Question.query.filter_by(course=course).count()
        answered = session.get('courses', {}).get(course.string, {}).get('answered', [])
    questions = set(range(1, num_questions + 1)) - set(answered) - {id}
    if questions:
        return random.choice(list(questions))
    else:
        # All questions have been answered
        return random.randint(1, num_questions + 1)


def session_data(session, index, model):
    if index not in session:
        session[index] = {}
    if model.string not in session[index].keys():
        session[index][model.string] = {'points': 0, 'total': 0, 'combo': 0, 'answered': []}
    return session[index][model.string]


def sort_exam(exam):
    """Silly way to sort exams by V09, H09, V10, H10 etc."""
    key = str(exam)
    if re.match(r'^V\d{2}$', key):
        key = key[1:3] + '1'
    elif re.match(r'^H\d{2}$', key):
        key = key[1:3] + '2'
    return key


@app.context_processor
def utility_processor():
    def percentage(num, total):
        if total > 0:
            return round((num * 100) / total, 2)
        return 0

    def grade(num, total):
        p = percentage(num, total)
        if total == 0:
            return '-'
        if p < 41:
            return 'F'
        elif p < 53:
            return 'E'
        elif p < 65:
            return 'D'
        elif p < 77:
            return 'C'
        elif p < 89:
            return 'B'
        else:
            return 'A'

    return dict(percentage=percentage, grade=grade)


if __name__ == '__main__':
    app.run()
