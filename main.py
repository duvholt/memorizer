from flask import abort, Flask, redirect, render_template, request, session, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug.contrib.fixers import ProxyFix
import json
import models
import os
import random

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.wsgi_app = ProxyFix(app.wsgi_app)
db = SQLAlchemy(app)


@app.route('/')
def main():
    context = {
        'courses': models.Course.query.all()
    }
    return render_template('courses.html', **context)


@app.route('/reset/<int:course_id>')
def reset_stats(course_id):
    """Reset stats for a course"""
    if 'courses' in session:
        if str(course_id) in session['courses']:
            del session['courses'][str(course_id)]
    return redirect(url_for('course', course_id=course_id))


@app.route('/<int:course_id>')
def course(course_id):
    """Redirects to a random question for a chosen course"""
    course = models.Course.query.get_or_404(course_id)
    return redirect(url_for('show_question', course_id=course_id, id=random_id(course)))


@app.route('/<int:course_id>/<int:id>', methods=['GET', 'POST'])
def show_question(course_id, id):
    if id == 0:
        return redirect(url_for('show_question', course_id=course_id, id=1))
    # Setting default value for session variables
    if 'courses' not in session:
        session['courses'] = {}
    if str(course_id) not in session['courses'].keys():
        session['courses'][str(course_id)] = {'points': 0, 'total': 0, 'combo': 0, 'answered': []}
    # Shortened variable
    c_session = session['courses'][str(course_id)]
    course = models.Course.query.filter_by(id=course_id).first_or_404()
    num_questions = models.Question.query.filter_by(course_id=course.id).count()
    if num_questions == 0:
        abort(404)
    context = {
        'alerts': [],
        'random': random_id(course, id),
        'prev': id - 1 if id > 1 else num_questions,
        'next': id + 1 if id < num_questions else 1,
        'num_questions': num_questions,
        'course': course
    }
    question = models.Question.query.filter_by(number=id - 1, course=course).first_or_404()
    context['question'] = question
    # Stupid hack (question.alternatives doesn't sort properly) TODO: Fix
    context['alternatives'] = models.Alternative.query.filter_by(question_id=question.id).order_by('number').all()
    # POST request when answering
    if request.method == 'POST':
        answer = request.form.get('answer')
        if answer:
            context['success'] = int(answer) == question.correct
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


@app.route('/import')
def import_questions():
    models.db.drop_all()
    models.db.create_all()
    for filename in os.listdir('questions'):
        with open('questions/' + filename, encoding='utf-8') as f:
            course_json = json.load(f)
        course = models.Course(course_json['code'], course_json['name'])
        questions = course_json['questions']
        db.session.add(course)
        db.session.commit()
        for i, question in enumerate(questions):
            question_object = models.Question(i, question['question'], course.id, question['correct'])
            db.session.add(question_object)
            db.session.commit()
            for number, answer in enumerate(question['answers']):
                alternative = models.Alternative(answer, number, question_object.id)
                db.session.add(alternative)
            db.session.commit()
    return redirect(url_for('main'))


def random_id(course, id=None):
    """Returns a random id from questions that have not been answered. Returns a complete random number if none available"""
    rand = id
    answered = session.get('courses', {}).get(str(course.id), {}).get('answered', [])
    num_questions = models.Question.query.filter_by(course_id=course.id).count()
    # All questions have been answered
    if num_questions == len(answered) or (id not in answered and num_questions == len(answered) + 1):
        return random.randint(1, num_questions)
    while rand in answered or rand in [id, None]:
        rand = random.randint(1, num_questions)
        print(rand)
    return rand


@app.context_processor
def utility_processor():
    def percentage(num, total):
        if total > 0:
            return round((num * 100) / total, 2)
        return 0
    return dict(percentage=percentage)

if __name__ == '__main__':
    app.run()
