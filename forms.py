import models
from flask_wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form

CourseForm = model_form(models.Course, Form)
ExamForm = model_form(models.Exam, Form)
QuestionForm = model_form(models.Question, Form)
