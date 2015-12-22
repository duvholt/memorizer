from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from logging.handlers import SMTPHandler
from werkzeug.contrib.fixers import ProxyFix
from views.admin import admin
from views.api import api
from views.quiz import quiz
from memorizer.cache import cache
from memorizer.utils import datetimeformat, grade, percentage
from memorizer.user import get_user
from memorizer.importer import ImportCommand
import logging


def create_app(config_filename='config.py'):
    from memorizer.database import db
    app = Flask(__name__)
    app.config.from_pyfile(config_filename)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    db.init_app(app)
    cache.init_app(app)
    migrate.init_app(app, db)
    manager(app)
    assets.init_app(app)

    app.register_blueprint(quiz)
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(api, url_prefix='/api')

    if app.debug:
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(app)
    else:
        app.logger.addHandler(mail_handler)

    @app.context_processor
    def utility_processor():
        return dict(percentage=percentage, grade=grade, user=get_user())

    app.jinja_env.filters['datetimeformat'] = datetimeformat
    return app


migrate = Migrate()
manager = Manager(create_app)
manager.add_command('db', MigrateCommand)
manager.add_command('import', ImportCommand)

assets = Environment()
js = Bundle(
    'js/ajax.js', 'js/collapse.js', 'js/alert.js', 'js/api.js', 'js/sidebar.js',
    'js/filter.js', filters='jsmin', output='js/min.%(version)s.js'
)
admin_js = Bundle('js/admin.js', 'js/question_form.js', filters='jsmin', output='js/admin.min.%(version)s.js')
app_js = Bundle('js/template.js', 'js/questions.js', filters='jsmin', output='js/app.min.%(version)s.js')
css = Bundle(
    'css/font-awesome.min.css', 'css/styles.css', 'css/admin.css',
    'css/form.css', 'css/collapse.css', filters='cssmin', output='css/min.%(version)s.css'
)
assets.register('js', js)
assets.register('admin_js', admin_js)
assets.register('app_js', app_js)
assets.register('css', css)

ADMINS = ['memorizer@cxhristian.com']
mail_handler = SMTPHandler(
    '127.0.0.1',
    'server-error@cxhristian.com',
    ADMINS, '[Flask] Memorizer ERROR'
)
mail_handler.setLevel(logging.ERROR)
