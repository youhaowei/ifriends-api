from flask_restful import reqparse, Resource
from validate_email import validate_email
from ..models.user import User


class UsersAPI(Resource):

    def __init__(self):
        self.postParser = reqparse.RequestParser()
        self.postParser.add_argument('email', required=True)
        self.postParser.add_argument('password', required=True)

    def get(self):
        pass

    def post(self):
        args = self.postParser.parse_args()
        if not validate_email(args['email']):
            return 'ERROR: email is not valid', 400
        try:
            result = User.register(args["email"], args["password"])
        except Exception as e:
            return str(e), 400
        return result
