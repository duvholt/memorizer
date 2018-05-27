from flask_wtf import FlaskForm
from wtforms import fields, validators
from wtforms_alchemy import model_form_factory

from memorizer import models

db = models.db
BaseModelForm = model_form_factory(FlaskForm)


class CourseForm(BaseModelForm):
    class Meta:
        model = models.Course


class ExamForm(BaseModelForm):
    class Meta:
        model = models.Exam

    # Foreign key
    course_id = fields.HiddenField()


class QuestionForm(BaseModelForm):
    class Meta:
        model = models.Question

    # Foreign key
    exam_id = fields.HiddenField()


class AlternativeForm(BaseModelForm):
    class Meta:
        model = models.Alternative

    # Foreign key
    question_id = fields.HiddenField()


class RegisterForm(FlaskForm):
    name = fields.StringField('Navn', [validators.Required()])
    username = fields.StringField('Brukernavn', [validators.Required()])
    password = fields.PasswordField('Passord', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passordene må være like')
    ])
    confirm = fields.PasswordField('Gjenta passord')


class LoginForm(FlaskForm):
    username = fields.StringField('Brukernavn', [validators.Required()])
    password = fields.PasswordField('Passord', [validators.Required()])
