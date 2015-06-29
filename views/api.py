from flask import abort, Blueprint, Response, request, session
from flask.views import MethodView
from views.admin import admin_required
import json
import models
import forms

api = Blueprint('api', __name__)


def error(message):
    return {'message': message}


class JsonView(MethodView):
    def dispatch_request(self, *args, **kwargs):
        """Returns a json document with mimetype set"""
        return Response(
            json.dumps(super(JsonView, self).dispatch_request(*args, **kwargs)),
            mimetype='application/json'
        )


class APIView(JsonView):
    model = None
    form = None

    def get(self, object_id=None):
        # Get a single object
        if object_id:
            object = self.model.query.get_or_404(object_id)
            return object.serialize()
        # Get all
        else:
            filters = {}
            # Filtering with query string parameters
            query = self.model.query
            for key in request.args.keys():
                model_columns = self.model.__table__.columns.keys()
                if key in model_columns:
                    value = request.args.getlist(key)
                    # SQL IN
                    if len(value) > 1:
                        # Not super pretty, but it works™
                        attr = getattr(self.model, key)
                        query = query.filter(attr.in_(value))
                    # SQL AND
                    else:
                        filters[key] = value[0]
            objects = query.filter_by(**filters)
            return [object.serialize() for object in objects]

    def post(self):
        response = {}
        if session.get('admin') is not True:
            response['errors'] = [error('Not logged in')]
            return response
        form = self.form(request.form)
        response['success'] = form.validate()
        if form.validate():
            # Inserting
            object = self.model()
            form.populate_obj(object)
            models.db.session.add(object)
            models.db.session.commit()
        else:
            response['errors'] = form.errors
        return response

    def put(self, object_id):
        response = {'success': False}
        if session.get('admin') is not True:
            response['errors'] = [error('Not logged in')]
            return response
        object = self.model.query.get(object_id)
        if not object:
            response['errors'] = [error('Item not found')]
            return response
        form = self.form(request.form, obj=object)
        form.populate_obj(object)
        response['success'] = form.validate()
        if response['success']:
            models.db.session.add(object)
            models.db.session.commit()
        else:
            response['errors'] = form.errors
        return response

    def delete(self, object_id):
        response = {}
        if session.get('admin') is not True:
            response['errors'] = [error('Not logged in')]
            return response
        object = self.model.query.get(object_id)
        if object:
            models.db.session.delete(object)
            models.db.session.commit()
        return {'success': bool(object)}


class CourseAPI(APIView):
    model = models.Course
    form = forms.CourseForm


class ExamAPI(APIView):
    model = models.Exam
    form = forms.ExamForm


class QuestionAPI(APIView):
    model = models.Question
    form = forms.QuestionForm


class AlternativeAPI(APIView):
    model = models.Alternative
    form = forms.AlternativeForm


def register_api(view, endpoint, url, pk='object_id', pk_type='int'):
    view_func = view.as_view(endpoint)
    api.add_url_rule(url, defaults={pk: None},
                     view_func=view_func, methods=['GET'])
    api.add_url_rule(url, view_func=view_func, methods=['POST'])
    api.add_url_rule('%s<%s:%s>' % (url, pk_type, pk), view_func=view_func,
                     methods=['GET', 'PUT', 'DELETE'])

register_api(CourseAPI, 'course_api', '/courses/')
register_api(ExamAPI, 'exam_api', '/exams/')
register_api(QuestionAPI, 'question_api', '/questions/')
register_api(AlternativeAPI, 'alterative_api', '/alternatives/')
