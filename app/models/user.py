from passlib.apps import custom_app_context as pwd_context
from .. import mongo
from itsdangerous import (
    JSONWebSignatureSerializer, TimedJSONWebSignatureSerializer,
    BadSignature, SignatureExpired
)
from flask import current_app
from bson import ObjectId
from enum import Enum


class Role(Enum):
    ADMIN = "Admin"
    MATCH_COORD = "Match Coordinator"
    CO_CHAIR = "Co-Chair"
    BOARD_MEMBER = "Board Member"
    CUR_STUDENT = "Student"
    PREV_STUDENT = "Previous Student"
    HOST = "Host"
    HOST_CANDIDATE = "Host Candidate"


class User:

    def __init__(self, uid):
        if isinstance(uid, str) or isinstance(uid, ObjectId):
            result = mongo.db.User.find_one({
                "_id": ObjectId(uid)
            }, {
                "email": 1,
                "password": 1,
                "roles": 1
            })
        else:
            result = uid
        if not result:
            raise Warning('User does not exist.')
        self.uid = uid
        self.email = result["email"]
        self.password = result["password"]
        self.roles = result["roles"]
        self.document = result

    @staticmethod
    def hash_password(password):
        return pwd_context.encrypt(password)

    @staticmethod
    def register(email, password, first_name, last_name):
        result = User.find_by_email(email)
        if result is not None:
            raise Warning("Email already exists.")
        result = mongo.db.User.insert_one({
            "email": email,
            "password": User.hash_password(password),
            "roles": [],
            "confirmed": False,
            "first_name": first_name,
            "last_name": last_name
        })
        s = TimedJSONWebSignatureSerializer(
            current_app.config["SECRET_KEY"], expires_in=900)
        return {
            "uid": str(result.inserted_id),
            "token": s.dumps({
                "uid": str(result.inserted_id)
            }).decode("ascii")
        }

    def generate_token(self, expire=900):
        # generate a timed token
        # default expired 15 minutes later
        s = TimedJSONWebSignatureSerializer(
            current_app.config["SECRET_KEY"], expires_in=expire)
        payload = {
            "uid": str(self.uid)
        }
        return s.dumps(payload)

    @staticmethod
    def verify_token(token):
        s = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        data = s.loads(token)
        user = User(data["uid"])
        return user

    @staticmethod
    def find_by_email(email):
        return mongo.db.User.find_one({
            "email": email
        }, {
            "_id": 1,
            "password": 1
        })

    @staticmethod
    def verify_password(email, password):
        result = User.find_by_email(email)
        if result is None:
            raise Warning("Email doesn't exist in database.")
        if pwd_context.verify(password, result['password']):
            return User(result["_id"])
        else:
            raise Warning("Invalid password")

    def update_host_info(self, update):
        update["host_pending"] = True
        mongo.db.User.update_one({
            "_id": ObjectId(self.uid)
        }, {
            "$set": update
        })
        return update

    def has_role(self, roles):
        if isinstance(roles, list):
            for role in roles:
                if role.value in self.roles:
                    return True
            return False
        else:
            return roles in self.roles
