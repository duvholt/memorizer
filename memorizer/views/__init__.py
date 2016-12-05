from flask import render_template
from flask.views import MethodView


class ContextMixin:
    def context(self, **kwargs):
        return kwargs


class TemplateMixin:
    template = None

    def get_template(self):
        return self.template


class TemplateView(TemplateMixin, ContextMixin):
    def dispatch_request(self, *args, **kwargs):
        return render_template(self.get_template(), **self.context(**kwargs))


class TemplateMethodView(TemplateMixin, ContextMixin, MethodView):
    def dispatch_request(self, *args, **kwargs):
        response = super().dispatch_request(*args, **kwargs)
        if response:
            return response
        return render_template(self.get_template(), **self.context(**kwargs))
