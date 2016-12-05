from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import FlaskPlugin
from sqlalchemy_utils import force_auto_coercion

from memorizer.utils import fetch_current_user_id

db = SQLAlchemy()

force_auto_coercion()
make_versioned(plugins=[FlaskPlugin(current_user_id_factory=fetch_current_user_id)])
