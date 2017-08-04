from flask_restful import reqparse, Resource
from validate_email import validate_email
from ..models.user import User, Role
from ..helpers import (
    role_required, token_required, TokenType, generate_token, token_missing
)
from .. import mongo
from ..email import send_email


class UsersAPI(Resource):

    def __init__(self):
        self.postParser = reqparse.RequestParser()
        self.postParser.add_argument('email', required=True)
        self.postParser.add_argument('password', required=True)
        self.postParser.add_argument('first_name', required=True)
        self.postParser.add_argument('last_name', required=True)

    def get(self):
        user = role_required([Role.ADMIN, Role.CO_CHAIR])
        query = mongo.db.User.find({})
        result = []
        for q in query:
            result.append({
                "_id": str(q["_id"]),
                "email": q["email"],
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
        uid = result["uid"]
        token = generate_token(900, {
            "type": TokenType.USER_CONFIRMATION.value,
            "uid": uid
        })
        send_email([args["email"]], "Please Confirm Your Account.",
                   'emails/out_user/confirm', token=token,
                   first_name=args["first_name"], uid=uid)
        return result


class UserConfirmAPI(Resource):

    def get(self, uid):
        user = User(uid)
        if token_missing():
            if user.confirmed:
                return "You have already confirmed your account."
            else:
                token = generate_token(900, {
                    "type": TokenType.USER_CONFIRMATION.value,
                    "uid": uid
                })
                send_email([user.email], "Please Confirm Your Account.",
                           'emails/out_user/confirm', token=token,
                           first_name=user.first_name, uid=uid)
                return "We have resent the email."
        token = token_required(TokenType.USER_CONFIRMATION)
        if uid != token["uid"]:
            abort(403, "Bad Token. This incident will be reported.")
        if user.confirmed:
            return "You have already confirmed your account."
        else:
            user.confirmed = True
            user.update()
            return "You have confirmed your account."
