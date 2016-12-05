from functools import wraps

from flask import g, redirect, request, session, url_for


def user_setup():
    """Set up user info for first time visitors"""
    from memorizer import models

    if 'user' in session:
        # Checking if user id actually exists
        user = models.User.query.get(session['user'])
        if user:
            return user
    user = models.User()
    models.db.session.add(user)
    models.db.session.commit()
    session['user'] = user.id
    # Set session to permament
    session.permanent = True
    return user


def get_user():
    user = getattr(g, 'user', None)
    if not user and not request.remote_addr:
        # TODO: None is returned here for SQLAlchemy-Continuum
        # when running cli commands
        return None
    if user is None:
        user = user_setup()
        g.user = user
    return user


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
