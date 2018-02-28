from passlib.apps import custom_app_context as pwd_context
from .. import mongo, login_manager
from itsdangerous import (
    JSONWebSignatureSerializer, TimedJSONWebSignatureSerializer,
    BadSignature, SignatureExpired
)
from flask import current_app, abort
from bson import ObjectId
from enum import Enum
from flask_login import UserMixin


def hash_password(password):
    return pwd_context.encrypt(password)


class Role(Enum):
    ADMIN = "Admin"
    MATCH_COORD = "Match Coordinator"
    CO_CHAIR = "Co-Chair"
    BOARD_MEMBER = "Board Member"
    CUR_STUDENT = "Student"
    PREV_STUDENT = "Previous Student"
    PENDING_STUDENT = "Pending Student"
    HOST = "Host"
    HOST_CANDIDATE = "Host Candidate"


"""
Model for user
"""


class User(UserMixin):

    """
    initiate user object from database with given user ID
    """

    def __init__(self, result):
        self.uid = result["_id"]
        self.email = result["email"]
        self.password = result["password"]
        self.roles = result["roles"]
        self.first_name = result["first_name"]
        self.last_name = result["last_name"]
        self.confirmed = result["confirmed"]
        self.document = result

    @staticmethod
    def load(uid):
        result = mongo.db.User.find_one({
            "_id": ObjectId(uid)
        })
        if not result:
            return None
        return User(result)

    """
    return a json string representing the user
    """

    def json(self):
        self.document["uid"] = str(self.uid)
        del self.document["_id"]
        return self.document

    """
    for flask_login, active user is confirmed user for now
    """

    def is_active(self):
        return self.confirmed

    """
    for flask_login
    """

    def get_id(self):
        return self.uid

    """
    register a new user, return the user object if successful
    """
    @staticmethod
    def register(email, password, first_name, last_name):
        result = User.find_by_email(email)
        if result is not None:
            raise Warning("Email already exists.")
        result = mongo.db.User.insert_one({
            "email": email,
            "password": hash_password(password),
            "roles": [],
            "confirmed": False,
            "first_name": first_name,
            "last_name": last_name
        })
        return User.load(result.inserted_id)

    """
    generate a token
    """

    def generate_token(self, expire=3600):
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
        user = User.load(data["uid"])
        return user

    @staticmethod
    def find_by_email(email):
        result = mongo.db.User.find_one({
            "email": email
        })
        if result is not None:
            return User(result)
        else:
            return result

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def update_host_info(self, update):
        if self.has_role(Role.HOST):
            abort(400, "Already a host!")
        else:
            self.add_role(Role.HOST_CANDIDATE)
            self.update()
        mongo.db.User.update_one({
            "_id": ObjectId(self.uid)
        }, {
            "$set": update
        })
        return update

    def update_student_info(self, update):
        if self.has_role(Role.CUR_STUDENT):
            abort(400, "Already a student!")
        else:
            self.add_role(Role.CUR_STUDENT)
            self.update()
        mongo.db.User.update_one({
            "_id": ObjectId(self.uid)
        }, {
            "$set": update
        })

    def add_role(self, role):
        if not self.has_role(role):
            self.roles.append(role.value)

    def remove_role(self, role):
        if self.has_role(role):
            self.roles.remove(role.value)

    def update(self):
        mongo.db.User.update_one({
            "_id": ObjectId(self.uid)
        }, {
            "$set": {
                "roles": self.roles,
                "confirmed": self.confirmed
            }
        })

    def has_role(self, roles):
        if isinstance(roles, list):
            for role in roles:
                if role.value in self.roles:
                    return True
            return False
        else:
            return roles.value in self.roles


@login_manager.user_loader
def load_user(user_id):
    return User.load(user_id)
