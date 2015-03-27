import models
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form

CourseForm = model_form(models.Course, base_class=Form)
ExamForm = model_form(models.Exam, base_class=Form)
QuestionForm = model_form(models.Question, base_class=Form)
