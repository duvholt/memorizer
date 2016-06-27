import argparse
import json

from flask_script import Command, Option

from memorizer import models
from memorizer.database import db


class ValidationError(Exception):
    pass


def import_question(question, exam):
    image = question.get('image', '')
    if 'answers' in question:
        question_type = models.Question.MULTIPLE
        answer = None
    else:
        question_type = models.Question.BOOLEAN
        answer = question['answer']
    question_object = models.Question(question_type, question['question'], exam.id, image, answer)
    db.session.add(question_object)
    db.session.commit()
    if question_type != models.Question.MULTIPLE:
        return
    for number, answer in enumerate(question['answers']):
        if type(question['correct']) is int and question['correct'] == number:
            correct = True
        elif type(question['correct']) is list and number in question['correct']:
            correct = True
        else:
            correct = False
        alternative = models.Alternative(answer, correct, question_object.id)
        db.session.add(alternative)
    db.session.commit()


def import_exam(exam_json):
    # Will raise exception if error found
    validate_exam(exam_json)
    # Get or create course
    course = models.Course.query.filter_by(code=exam_json['code']).first()
    if not course:
        course = models.Course(exam_json['code'], exam_json['name'])
        db.session.add(course)
        db.session.commit()
    # Get or create exam
    exam = models.Exam.query.filter_by(name=exam_json['exam'], course=course).first()
    if not exam:
        exam = models.Exam(exam_json['exam'], course.id)
        db.session.add(exam)
        db.session.commit()
    questions = exam_json['questions']
    for question_json in questions:
        import_question(question_json, exam)
    return True


def validate_exam(exam_json):
    # Exam name and course code has to present
    if 'code' not in exam_json:
        raise ValidationError('Emnekode mangler')
    if type(exam_json['code']) is not str:
        raise ValidationError('Emnekode må være tekst')
    if len(exam_json['code']) == 0:
        raise ValidationError('Emnekode kan ikke være tomt')
    if 'name' not in exam_json:
        raise ValidationError('Emnenavn mangler')
    if type(exam_json['name']) is not str:
        raise ValidationError('Emnenavn må være tekst')
    if len(exam_json['name']) == 0:
        raise ValidationError('Emnenavn kan ikke være tomt')
    if 'exam' not in exam_json:
        raise ValidationError('Eksamensnavn mangler')
    if type(exam_json['exam']) is not str:
        raise ValidationError('Eksamensnavn må være tekst')
    if len(exam_json['exam']) == 0:
        raise ValidationError('Eksamensnavn kan ikke være tomt')
    validate_questions(exam_json)


def validate_questions(exam_json):
    if 'questions' not in exam_json:
        raise ValidationError('Spørsmål mangler')
    if type(exam_json['questions']) is not list:
        raise ValidationError('Spørsmål må være en liste')
    if len(exam_json['questions']) == 0:
        raise ValidationError('Det må være minst et spørsmål')
    questions = exam_json['questions']
    for question in questions:
        try:
            validate_question(question)
        except ValidationError as e:
            # Reraising with more information
            raise ValidationError('{}: {}'.format(e, question.get('question')))


def _validate_alternative(answer):
    if type(answer) is not str:
        raise ValidationError('Alle alternativer med være tekst')
    if len(answer) == 0:
        raise ValidationError('Alternativ kan ikke være tomt')


def _validate_correct_answers(answer, length):
    if type(answer) is not int:
        raise ValidationError('Riktige svar må være integer eller liste med integere')
    if not (0 <= answer < length):
        raise ValidationError('Et av de riktige svarene stemmer ikke overens med noen alternativer')


def _validate_multiple_answers(question):
    if type(question['answers']) is not list:
        raise ValidationError('Alternativer må være en liste')
    if len(question['answers']) < 2:
        raise ValidationError('Det må være minst to alternativer')
    if 'correct' not in question:
        raise ValidationError('Spørsmål mangler riktig(e) svar')
    if type(question['correct']) is int:
        answers = [question['correct']]
    elif type(question['correct']) is list:
        answers = question['correct']
    else:
        raise ValidationError('Riktig svar må være integer eller en liste med integere')
    if len(answers) == 0:
        raise ValidationError('Det må være minst et riktig svar')
    for answer in question['answers']:
        _validate_alternative(answer)
    for answer in answers:
        _validate_correct_answers(answer, len(question['answers']))


def validate_question(question):
    if 'question' not in question:
            raise ValidationError('Spørsmålstekst mangler')
    if type(question['question']) is not str:
        raise ValidationError('Spørsmål må være tekst')
    if len(question['question']) == 0:
        raise ValidationError('Spørsmål kan ikke være tomt')
    if 'answers' in question:
        # Multiple answers
        _validate_multiple_answers(question)
    elif 'answer' in question:
        # Boolean answer
        if type(question['answer']) is not bool:
            raise ValidationError('Svar må være "true" eller "false"')
    else:
        raise ValidationError('Svar mangler')


class ImportCommand(Command):
    'Import questions in JSON format'

    option_list = (
        Option('filenames', nargs='+', type=argparse.FileType('r'), help='JSON question files'),
    )

    def run(self, filenames):
        print("Importing questions...")
        for filename in filenames:
            exam_json = json.load(filename)
            print('Importing questions from', exam_json['name'], exam_json['code'], 'exam', exam_json['exam'])
            import_exam(exam_json)
        print("Importing completed")
