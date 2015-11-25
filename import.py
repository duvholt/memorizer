#!/usr/bin/env python3
from memorizer.application import app, db
from memorizer import models
import argparse
import json


def import_questions(filename):
    course_json = json.load(filename)
    print('Importing questions from', course_json['name'], course_json['code'], 'exam', course_json['exam'])
    # Get or create course
    course = models.Course.query.filter_by(code=course_json['code'], name=course_json['name']).first()
    if not course:
        course = models.Course(course_json['code'], course_json['name'])
        db.session.add(course)
        db.session.commit()
    # Get or create exam
    exam = models.Exam.query.filter_by(name=course_json['exam'], course=course).first()
    if not exam:
        exam = models.Exam(course_json['exam'], course.id)
        db.session.add(exam)
        db.session.commit()
    questions = course_json['questions']
    for question in questions:
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
            continue
        for number, answer in enumerate(question['answers']):
            if type(question['correct']) is int and question['correct'] == number:
                correct = True
            elif type(question['correct']) is list and number in question['correct']:
                correct = True
            else:
                correct = False
            # Setting image if it exists
            alternative = models.Alternative(answer, correct, question_object.id)
            db.session.add(alternative)
        db.session.commit()

parser = argparse.ArgumentParser(description='Import questions in JSON format')
parser.add_argument('filenames', nargs='+', type=argparse.FileType('r'), help='JSON question files')
args = parser.parse_args()

if __name__ == '__main__':
    print("Importing questions...")
    with app.app_context():
        for filename in args.filenames:
            import_questions(filename)
        print("Importing completed")
