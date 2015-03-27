import models
from flask.ext.wtf import Form
from wtforms.ext.sqlalchemy.orm import model_form

db_session = models.db.session

CourseForm = model_form(models.Course, db_session=db_session, base_class=Form)
ExamForm = model_form(models.Exam, db_session=db_session, base_class=Form)
QuestionForm = model_form(models.Question, db_session=db_session, base_class=Form)
