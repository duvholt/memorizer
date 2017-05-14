import random
import re

from memorizer import models
from memorizer.cache import cache
from memorizer.config import CACHE_TIME
from memorizer.user import get_user


@cache.memoize(CACHE_TIME)
def max_questions_exam(course_code, exam_name):
    return models.Question.query.\
        join(models.Exam).join(models.Course).\
        filter_by(code=course_code).\
        filter(models.Exam.name == exam_name).count()


@cache.memoize(CACHE_TIME)
def max_questions_course(course_code):
    return models.Question.query.\
        join(models.Exam).join(models.Course).\
        filter_by(code=course_code).count()


def generate_stats(course_code, exam_name=None):
    stats_data = {}
    if not exam_name:
        stats_data['max'] = max_questions_course(course_code)
        stats = models.Stats.course(get_user(), course_code)
    else:
        stats_data['max'] = max_questions_exam(course_code, exam_name)
        stats = models.Stats.exam(get_user(), course_code, exam_name)
    stats_all = stats.all()
    stats_data['total'] = len(stats_all)
    stats_data['points'] = len(list(filter(lambda stat: stat.correct, stats_all)))
    stats_data['grade'] = grade(stats_data['points'], stats_data['total'])
    stats_data['percentage'] = percentage(stats_data['points'], stats_data['total'])

    combo = 0
    for stat in reversed(stats_all):
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
    query = models.db.session.query(models.Question.id).distinct().\
        join(models.Exam).join(models.Course)
    if exam:
        query = query.filter(models.Exam.name == exam)
    elif course:
        query = query.filter(models.Course.code == course)
    # All questions
    questions = query.all()
    # Already answered questions
    answered = set(
        query.join(models.Stats)
        .filter(models.Stats.reset.is_(False), models.Stats.user_id == get_user().id)
        .all()
    )
    # List of indexes for unanswered questions
    indexes = [i for i, question in enumerate(questions) if question not in answered]
    if indexes:
        # Select random index
        return random.choice(indexes) + 1
    else:
        # All questions have been answered
        return random.randint(1, len(questions) + 1)


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
            return round((num * 100) / total)
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


def datetimeformat(value, format='%Y-%m-%d %H:%M'):
    return value.strftime(format)
