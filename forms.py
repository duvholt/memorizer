import models
from flask.ext.wtf import Form
from wtforms_alchemy import model_form_factory
from wtforms.fields import HiddenField

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

    # Foreign key
    course_id = HiddenField()


class QuestionForm(ModelForm):
    class Meta:
        model = models.Question

    # Foreign key
    exam_id = HiddenField()


class AlternativeForm(ModelForm):
    class Meta:
        model = models.Alternative

    # Foreign key
    question_id = HiddenField()
