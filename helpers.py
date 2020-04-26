from flask import redirect, session
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login
    :param f:
    :return: decorated_function()
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function
