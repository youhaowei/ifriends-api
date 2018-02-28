from flask import Blueprint, request, jsonify
from .user import UsersAPI, UserConfirmAPI, UserAPI
from .host import HostsAPI, HostVerifyAPI
from .student import StudentsAPI
from flask_restful import Api
from ..models import User


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

api.add_resource(UsersAPI, '/users')
api.add_resource(UserConfirmAPI, '/user/<uid>/confirm',
                 endpoint='user_confirm')
api.add_resource(UserAPI, '/user/<uid>')

api.add_resource(HostsAPI, "/hosts")

api.add_resource(StudentsAPI, '/students')

api.add_resource(HostVerifyAPI, '/host/<uid>/verify', endpoint='host_verify')

"""
OLD API for login
return user info and token if success
"""


@api_bp.route("/token", methods=["POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            user = User.find_by_email(email)
            if user.verify_password(password):
                return jsonify({
                    "token": str(user.generate_token().decode("ascii")),
                    "uid": str(user.uid),
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                })
            else:
                return "Wrong password.", 400
        except Exception as e:
            return str(e), 400

    else:
        return None
