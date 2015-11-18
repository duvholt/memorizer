from flask import session
import models
import random
import re
from user import get_user


def generate_stats(course_code, exam_name=None):
    stats_data = {}
    if not exam_name:
        stats_data['max'] = models.Question.query.\
            join(models.Exam).join(models.Course).\
            filter_by(code=course_code).count()
        stats = models.Stats.course(get_user(), course_code)
    else:
        stats_data['max'] = models.Question.query.\
            join(models.Exam).join(models.Course).\
            filter_by(code=course_code).\
            filter(models.Exam.name == exam_name).count()
        stats = models.Stats.exam(get_user(), course_code, exam_name)
    stats_data['total'] = stats.count()
    stats_data['points'] = stats.filter(models.Stats.correct == True).count()
    # TODO: Clean up this
    stats_data['answered'] = list({stat.question.id for stat in stats.all()})
    stats_data['grade'] = grade(stats_data['points'], stats_data['total'])
    stats_data['percentage'] = percentage(stats_data['points'], stats_data['total'])

    combo = 0
    for stat in reversed(stats.all()):
        if stat.correct:
            combo += 1
        else:
            break
    stats_data['combo'] = combo
    return stats_data


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
