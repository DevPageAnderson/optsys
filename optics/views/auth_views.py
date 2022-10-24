import functools
from flask import redirect, url_for, Blueprint, g

bp = Blueprint('auth', __name__, url_prefix='/auth')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kargs):
        if g.user is None:
            return redirect(url_for('main.log_in'))
        return view(**kargs)
    return wrapped_view