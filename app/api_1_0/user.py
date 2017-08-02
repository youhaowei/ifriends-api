from flask_restful import reqparse, Resource
from validate_email import validate_email
from ..models.user import User, Role
from ..decorators import role_required
from .. import mongo


class UsersAPI(Resource):

    def __init__(self):
        self.postParser = reqparse.RequestParser()
        self.postParser.add_argument('email', required=True)
        self.postParser.add_argument('password', required=True)
        self.postParser.add_argument('first_name', required=True)
        self.postParser.add_argument('last_name', required=True)

    @role_required([Role.ADMIN, Role.CO_CHAIR])
    def get(self):
        query = mongo.db.find({})
        result = []
        for q in query:
            result.append({
                "_id": str(q["_id"]),
                "email": q["email"]
                "roles": q["roles"]
            })
        return result

    def post(self):
        args = self.postParser.parse_args()
        if not validate_email(args['email']):
            return 'ERROR: email is not valid', 400
        try:
            result = User.register(
                args["email"], args["password"], 
                args["first_name"], args["last_name"])
        except Exception as e:
            return str(e), 400
        return result
