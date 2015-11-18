from flask import _request_ctx_stack, redirect, session, url_for
from functools import wraps
import models


def user_setup():
    """Set up user info for first time visitors"""
    if 'user' in session:
        # Checking if user id actually exists
        user = models.User.query.get(session['user'])
        if user:
            return
    user = models.User()
    models.db.session.add(user)
    models.db.session.commit()
    session['user'] = user.id
    # Set session to permament
    session.permanent = True


def get_user():
    ctx = _request_ctx_stack.top
    if not hasattr(_request_ctx_stack.top, 'user'):
        user_setup()
        ctx.user = models.User.query.get(session['user'])
    return ctx.user


# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_user()
        if not user.registered:
            return redirect(url_for('quiz.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = get_user()
        if not user.admin:
            return redirect(url_for('admin.index'))
        return f(*args, **kwargs)
    return decorated_function
