from flask import Flask
from flask.ext.assets import Environment, Bundle
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand
from logging.handlers import SMTPHandler
from memorizer.models import db
from werkzeug.contrib.fixers import ProxyFix
from views.admin import admin
from views.api import api
from views.quiz import quiz
from memorizer.cache import cache
from memorizer.utils import grade, percentage
from memorizer.user import get_user
import logging

app = Flask(__name__)
app.config.from_pyfile('config.py')
app.wsgi_app = ProxyFix(app.wsgi_app)
db.init_app(app)
cache.init_app(app)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

assets = Environment(app)
js = Bundle(
    'js/ajax.js', 'js/collapse.js', 'js/alert.js', 'js/api.js', 'js/sidebar.js',
    'js/filter.js', filters='jsmin', output='js/min.%(version)s.js'
)
admin_js = Bundle('js/admin.js', filters='jsmin', output='js/admin.min.%(version)s.js')
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
if not app.debug:
    mail_handler = SMTPHandler('127.0.0.1',
                               'server-error@cxhristian.com',
                               ADMINS, '[Flask] Memorizer ERROR')
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)

app.register_blueprint(quiz)
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(api, url_prefix='/api')


@app.context_processor
def utility_processor():
    return dict(percentage=percentage, grade=grade, user=get_user())
