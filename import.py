#!/usr/bin/env python3
from main import app, db
import models
import json
import os


def import_questions():
    # TODO: Proper importing with migrations
    # Reset database
    models.db.drop_all()
    models.db.create_all()
    # Load exams from folder with json files
    for filename in os.listdir('questions'):
        if os.path.isdir(os.path.join('questions', filename)):
            # Skip folders
            continue
        with open('questions/' + filename, encoding='utf-8') as f:
            course_json = json.load(f)
        print('Importing questions from', course_json['name'], course_json['code'])
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
            image = question['image'] if 'image' in question else ""
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
    print("Importing completed")


if __name__ == '__main__':
    print("Importing questions...")
    with app.app_context():
        import_questions()
