from flask import session
import models
import random
import re


def stats(index, model):
    if index not in session:
        session[index] = {}
    if model.string not in session[index].keys():
        session[index][model.string] = {'points': 0, 'total': 0, 'combo': 0, 'answered': []}
    stats_data = session[index][model.string]
    stats_data['grade'] = grade(stats_data['points'], stats_data['total'])
    stats_data['percentage'] = percentage(stats_data['points'], stats_data['total'])
    return stats_data


def save_answer(course, question_id, correct):
    """Sets session data and returns if question has already been answered"""
    c_session = stats('courses', course)
    if question_id not in c_session['answered']:
        c_session['points'] += int(correct)
        c_session['answered'].append(question_id)
        c_session['total'] = len(c_session['answered'])
        if correct:
            c_session['combo'] += 1
        else:
            c_session['combo'] = 0
        return False
    return True


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


def sort_exam(exam):
    """Silly way to sort exams by V09, H09, V10, H10 etc."""
    key = str(exam)
    if re.match(r'^V\d{2}$', key):
        key = key[1:3] + '1'
    elif re.match(r'^H\d{2}$', key):
        key = key[1:3] + '2'
    return key


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
