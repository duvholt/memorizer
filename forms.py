import models
from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory

db = models.db
BaseModelForm = model_form_factory(Form)


class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session


class CourseForm(ModelForm):
    class Meta:
        model = models.Course


class ExamForm(ModelForm):
    class Meta:
        model = models.Exam


class QuestionForm(ModelForm):
    class Meta:
        model = models.Question
