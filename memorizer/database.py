from flask import _request_ctx_stack
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_continuum import make_versioned
from sqlalchemy_continuum.plugins import FlaskPlugin
from sqlalchemy_utils import force_auto_coercion

from memorizer.user import get_user


def fetch_current_user_id():
    # Return None if we are outside of request context.
    if _request_ctx_stack.top is None:
        return
    return getattr(get_user(), 'id', None)


db = SQLAlchemy()

force_auto_coercion()
make_versioned(plugins=[FlaskPlugin(current_user_id_factory=fetch_current_user_id)])
