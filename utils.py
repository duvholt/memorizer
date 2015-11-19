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
    stats_data['points'] = stats.filter(models.Stats.correct.is_(True)).count()
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
    query = models.db.session.query(models.Question.id).distinct().\
        join(models.Exam).join(models.Course).join(models.Stats)
    if exam:
        query = query.filter(models.Exam.name == exam.name)
    elif course:
        query = query.filter(models.Course.code == course.code)
    # All questions
    questions = query.all()
    # Already answered questions
    answered = set(query.filter(models.Stats.reset.is_(False), models.Stats.user_id == get_user().id).all())
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
