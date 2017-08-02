from functools import wraps
from flask import request, g, abort
from .models import User


def role_required(f):
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
        return True
    else:
        abort(503)


def token_required():
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
    return user
    
