from functools import wraps
from flask import request, g, abort, current_app
from .models.user import User
from itsdangerous import (
    JSONWebSignatureSerializer, TimedJSONWebSignatureSerializer,
    BadSignature, SignatureExpired
)
from enum import Enum


class TokenType(Enum):
    USER_AUTHENTICATION = 0
    USER_CONFIRMATION = 1
    HOST_VERIFICATION = 2


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
        abort(401, "Missing User Token.")

    try:
        user = User.verify_token(token)
    except Exception as e:
        abort(400, "Bad User Token: " + str(e))
    if user.has_role(f):
        return user
    else:
        abort(401)


def auth_required():
    try:
        if request.is_json:
            token = request.json["token"]
        else:
            token = request.values["token"]
    except:
        abort(401, "Missing User Token.")
    try:
        user = User.verify_token(token)
    except Exception as e:
        abort(400, "Bad User Token: " + str(e))
    return user


def token_required(type):
    try:
        if request.is_json:
            token = request.json["token"]
        else:
            token = request.values["token"]
    except:
        abort(401, "Missing Token.")
    token = decode_token(token)
    if not type:
        return token
    if TokenType(token["type"]) != type:
        abort(400, "Bad Token Type: " + str(token["type"]))
    else:
        return token


def token_missing():
    try:
        if request.is_json:
            token = request.json["token"]
        else:
            token = request.values["token"]
    except:
        return True
    else:
        return False
