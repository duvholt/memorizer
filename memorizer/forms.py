from flask_wtf import FlaskForm
from wtforms import fields, validators
from wtforms_alchemy import model_form_factory

from memorizer import models
from memorizer.user import get_user

db = models.db
BaseModelForm = model_form_factory(FlaskForm)


class MemorizerForm:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.remove_admin_fields()

    def remove_admin_fields(self):
        user = get_user()
        delete_fields = []
        for field in self:
            name = field.name
            model_field = getattr(field.meta.model, name, None)
            if not model_field:
                continue
            if 'admin' in model_field.info and model_field.info['admin']:
                if not user.admin:
                    delete_fields.append(name)
        for field in delete_fields:
            delattr(self, field)


class CourseForm(MemorizerForm, BaseModelForm):
    class Meta:
        model = models.Course


class ExamForm(MemorizerForm, BaseModelForm):
    class Meta:
        model = models.Exam

    # Foreign key
    course_id = fields.HiddenField()


class QuestionForm(MemorizerForm, BaseModelForm):
    class Meta:
        model = models.Question

    # Foreign key
    exam_id = fields.HiddenField()


class AlternativeForm(MemorizerForm, BaseModelForm):
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
