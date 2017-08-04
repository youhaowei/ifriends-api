from functools import wraps
from flask import request, g, abort
from .models.user import User
from itsdangerous import (
    JSONWebSignatureSerializer, TimedJSONWebSignatureSerializer,
    BadSignature, SignatureExpired
)


def generate_token(expire, payload):
    s = TimedJSONWebSignatureSerializer(
        current_app.config["SECRET_KEY"], expires_in=expire)
    return s.dumps(payload)


def decode_token(token):
    s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
    return s.loads(token)


def role_required(f):
    try:
        if request.is_json:
            token = request.json["token"]
        else:
            token = request.values["token"]
    except:
        abort(400, "Missing User Token.")

    try:
        user = User.verify_token(token)
    except Exception as e:
        abort(400, "Bad User Token: " + str(e))
    if user.has_role(f):
        return user
    else:
        abort(403)


def token_required():
    try:
        if request.is_json:
            token = request.json["token"]
        else:
            token = request.values["token"]
    except:
        abort(400, "Missing User Token.")
    try:
        user = User.verify_token(token)
    except Exception as e:
        abort(400, "Bad User Token: " + str(e))
    return user
