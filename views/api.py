from flask import abort, Blueprint, Response, request
from flask.views import MethodView
from views.admin import admin_required
import json
import models

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
    fields = []

    def get(self, object_id=None):
        # Get a single object
        if object_id:
            object = self.model.query.get_or_404(object_id)
            return object.serialize()
        # Get all
        else:
            filters = {}
            # Filtering with query string parameters
            for key, value in request.args.items():
                if hasattr(self.model, key):
                    filters[key] = value
            objects = self.model.query.filter_by(**filters)
            return [object.serialize() for object in objects]

    def post(self):
        errors = []
        for field in self.fields:
            if field not in request.form.keys():
                errors.append(error('Missing field ' + field))
        # If all fields are present
        if not errors:
            errors = self.validate()
        if errors:
            return {'errors': errors}
        else:
            # Inserting
            object = self.model(**self.post_dict(request.form))
            models.db.session.add(object)
            models.db.session.commit()
        return {'success': True}

    def put(self, object_id):
        errors = []
        object = self.model.query.get(object_id)
        if not object:
            return {'errors': [error('Item not found')]}
        for field in self.fields:
            if field not in request.form.keys():
                errors.append(error('Missing field ' + field))
        if not errors:
            errors = self.validate()
        if errors:
            return {'errors': errors}
        for field in self.fields:
            setattr(object, field, request.form[field])
            models.db.session.commit()
        return {'success': True}


    def delete(self, object_id):
        object = self.model.query.get(object_id)
        if object:
            models.db.session.delete(object)
            models.db.session.commit()
        return {'success': bool(object)}

    def validate(self):
        """Return a list of errors"""
        return []

    def post_dict(self, post_data):
        """Dictionary of fields with form data"""
        return {field: post_data[field] for field in self.fields}


class CourseAPI(APIView):
    model = models.Course
    fields = ['name', 'code']

    def validate(self):
        errors = []
        for field in self.fields:
            if len(request.form[field]) == 0:
                errors.append(error('"' + field + '" length has to be bigger than zero'))
        result = self.model.query.filter_by(code=request.form['code']).first()
        if result:
            errors.append(error('Course code is already taken'))
        return errors


class ExamAPI(APIView):
    model = models.Exam


class QuestionAPI(APIView):
    model = models.Question


class AlternativeAPI(APIView):
    model = models.Alternative


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
