from flask import Blueprint
from .user import UsersAPI, UserConfirmAPI, UserAPI
from .host import HostsAPI, HostVerifyAPI
from .student import StudentsAPI
from flask_restful import Api


api_bp = Blueprint('api', __name__)
api = Api(api_bp)

api.add_resource(UsersAPI, '/users')
api.add_resource(UserConfirmAPI, '/user/<uid>/confirm',
                 endpoint='user_confirm')
api.add_resource(UserAPI, '/user/<uid>')

api.add_resource(HostsAPI, "/hosts")

api.add_resource(StudentsAPI, '/students')

api.add_resource(HostVerifyAPI, '/host/<uid>/verify', endpoint='host_verify')
