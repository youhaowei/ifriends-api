from functools import wraps
from flask import request, g
from .models import User


def role_required(f):
    @wraps(f)
    def decorated_function(*args, **wkargs):
        if not g.user:
            try:
                if request.is_json:
                    token = request.json["token"]
                else:
                    token = request.values["token"]
            except:
                abort(400, "Bad or Missing Token.")
                
            try:
                user = User.verify_token(token)
            except:
                abort(400, "Bad Token.")
            g.user = user
        else:
            user = g.user
        if user.has_role(f):
            return f(*args, **kwargs)
    return decorated_function


def registration_required(f):
    @wraps(f)
    def decorated_function(*args, **wkargs):
        try:
            if request.is_json:
                token = request.json["token"]
            else:
                token = request.values["token"]
        except:
            abort(400, "Missing Token.")
        try:
            user = User.verify_token(token)
        except:
            abort(400, "Bad Token.")
        g.user = user
        return f(*args, **kwargs)
    return decorated_function
