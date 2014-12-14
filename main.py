#!/usr/bin/env python3
from flask import abort, Flask, redirect, render_template, request, session, url_for
from models import db
from werkzeug.contrib.fixers import ProxyFix
import json
import models
import os
import random
import re

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.wsgi_app = ProxyFix(app.wsgi_app)
db.init_app(app)


@app.route('/')
def main():
    context = {
        'courses': sort_courses(models.Course.query.options(db.joinedload('exams')).all()),
        'breadcrumbs': [{'name': 'Emner'}]
    }
    return render_template('courses.html', **context)


@app.route('/reset/<string:course_code>/')
def reset_stats_course(course_code):
    """Reset stats for a course"""
    if 'courses' in session:
        course = models.Course.query.filter_by(code=course_code).first()
        if course and str(course_code) in session['courses']:
            del session['courses'][str(course_code)]
    return redirect(url_for('course', course_code=course_code))


@app.route('/reset/<string:course_code>/<string:exam_name>/')
def reset_stats_exam(course_code, exam_name):
    """Reset stats for a course"""
    if 'exams' in session:
        if exam and course_code + '_' + exam_name in session['exams']:
            del session['exams'][course_code + '_' + exam_name]
    return redirect(url_for('exam', course_code=course_code, exam_name=exam_name))


@app.route('/<string:course_code>/')
def course(course_code):
    """Redirects to a random question for a chosen course"""
    course = models.Course.query.filter_by(code=course_code).first_or_404()
    return redirect(url_for('show_question', course_code=course_code, exam_name='all', id=random_id(course=course)))


@app.route('/<string:course_code>/<string:exam_name>/')
def exam(course_code, exam_name):
    """Redirects to a random question for a chosen exam"""
    course = models.Course.query.filter_by(code=course_code).first_or_404()
    exam = models.Exam.query.filter_by(course=course, name=exam_name).first_or_404()
    return redirect(url_for('show_question', course_code=course_code, exam_name=exam.name, id=random_id(exam=exam)))


@app.route('/<string:course_code>/<string:exam_name>/<int:id>', methods=['GET', 'POST'])
def show_question(course_code, exam_name, id):
    if id == 0:
        return redirect(url_for('show_question', course_code=course_code, exam_name=exam_name, id=1))
    # Setting default value for session variables
    course = models.Course.query.filter_by(code=course_code).first_or_404()
    if exam_name != 'all':
        exam = models.Exam.query.filter_by(course=course, name=exam_name).first_or_404()
        if 'exams' not in session:
            session['exams'] = {}
        if course_code + '_' + exam_name not in session['exams'].keys():
            session['exams'][course_code + '_' + exam_name] = {'points': 0, 'total': 0, 'combo': 0, 'answered': []}
        # Shortened variable
        c_session = session['exams'][course_code + '_' + exam_name]
        # Only question from a specific exam
        num_questions = models.Question.query.filter_by(exam=exam).count()
        question = models.Question.query.filter_by(exam=exam).order_by(models.Question.id).offset(id - 1).limit(1).first_or_404()
        reset_url = url_for('reset_stats_exam', course_code=course.code, exam_name=exam.name)
        breadcrumbs = [
            {'name': 'Emner', 'url': url_for('main')},
            {'name': course, 'url': url_for('course', course_code=course_code)},
            {'name': exam}
        ]
    else:
        if 'courses' not in session:
            session['courses'] = {}
        if course_code not in session['courses'].keys():
            session['courses'][course_code] = {'points': 0, 'total': 0, 'combo': 0, 'answered': []}
        # Shortened variable
        c_session = session['courses'][course_code]
        # All questions
        exam = None
        num_questions = models.Question.query.filter_by(course=course).count()
        question = models.Question.query.filter_by(course=course).offset(id - 1).limit(1).first_or_404()
        reset_url = url_for('reset_stats_course', course_code=course.code)
        breadcrumbs = [
            {'name': 'Emner', 'url': url_for('main')},
            {'name': str(course) + ' - ' + str(question.exam)}
        ]
    if num_questions == 0:
        abort(404)
    context = {
        'id': id,
        'alerts': [],
        'random': random_id(id=id, course=course, exam=exam),
        'prev': id - 1 if id > 1 else num_questions,
        'next': id + 1 if id < num_questions else 1,
        'num_questions': num_questions,
        'course': course,
        'exam_name': exam_name,
        'reset_url': reset_url,
        'breadcrumbs': breadcrumbs
    }
    context['question'] = question
    # Stupid hack (question.alternatives doesn't sort properly) TODO: Fix
    context['alternatives'] = models.Alternative.query.filter_by(question_id=question.id).order_by('number').all()
    # POST request when answering
    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer:
            for alternative in context['alternatives']:
                if str(alternative.number) == answer:
                    context['success'] = alternative.correct
                    break
            # Checking if question has already been answered
            if id not in c_session['answered']:
                c_session['points'] += int(context['success'])
                c_session['total'] += 1
                c_session['answered'].append(id)
                if not context['success']:
                    c_session['combo'] = 0
                else:
                    c_session['combo'] += 1
            elif context['success']:
                context['alerts'].append({'msg': 'Du har allerede svart på dette spørsmålet så du får ikke noe poeng. :-)', 'level': 'info'})
        else:
            context['alerts'].append({'msg': 'Blankt svar', 'level': 'danger'})
        # Preserving order on submit
        ordering = request.form.get('order')
        if ordering:
            # Resorting answers from specific values. Answer is a tuple with id and texts
            context['alternatives'] = [context['alternatives'][int(x)] for x in ordering.split(',')]
    else:
        # Random order on questions
        random.shuffle(context['alternatives'])
    context['score'] = c_session
    return render_template('question.html', **context)


def random_id(id=None, course=None, exam=None):
    """Returns a random id from questions that have not been answered. Returns a complete random number if none available"""
    rand = id
    if exam:
        num_questions = models.Question.query.filter_by(exam=exam).count()
        answered = session.get('exams', {}).get(str(exam.id), {}).get('answered', [])
    elif course:
        num_questions = models.Question.query.filter_by(course=course).count()
        answered = session.get('courses', {}).get(str(course.id), {}).get('answered', [])
    # All questions have been answered
    if num_questions == len(answered) or (id not in answered and num_questions == len(answered) + 1):
        return random.randint(1, num_questions)
    while rand in answered or rand in [id, None]:
        rand = random.randint(1, num_questions)
        print(rand)
    return rand


def sort_courses(courses):
    sorted_courses = []
    for course in courses:
        course.exams.sort(key=sort_exam)
        sorted_courses.append(course)
    return sorted_courses


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
    return dict(percentage=percentage)


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                     endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


if __name__ == '__main__':
    app.run()
