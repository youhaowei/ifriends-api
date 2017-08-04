from flask_restful import reqparse, Resource
from ..helpers import (
    auth_required, role_required, generate_token, TokenType, token_required
)
from ..email import send_email
from ..models import Role
from .. import mongo
from ..models import User


class HostsAPI(Resource):

    def __init__(self):
        """ first page """
        self.postParser = reqparse.RequestParser()
        self.postParser.add_argument('first_name', required=True)
        self.postParser.add_argument('last_name', required=True)
        self.postParser.add_argument('email', required=True)
        self.postParser.add_argument('spouse_first_name')
        self.postParser.add_argument('spouse_last_name')
        self.postParser.add_argument('gender', required=True)
        self.postParser.add_argument("occupation", required=True)
        self.postParser.add_argument("spouse_occupation")
        self.postParser.add_argument("address", required=True)
        self.postParser.add_argument('phone', required=True)
        self.postParser.add_argument('best_contact', required=True)
        self.postParser.add_argument('has_facebook', required=True, type=bool)
        self.postParser.add_argument('add_facebook', type=bool)
        self.postParser.add_argument('hear_about_us', required=True)

        """ second page """
        self.postParser.add_argument('household_size', required=True, type=int)
        self.postParser.add_argument('has_children', required=True, type=bool)
        self.postParser.add_argument('children_age')
        self.postParser.add_argument('has_pets', required=True, type=bool)
        self.postParser.add_argument('pets')
        self.postParser.add_argument('smoker', required=True, type=bool)

        """ third page """
        # Serve on the International Friends Board or a Comittee
        self.postParser.add_argument('help_board', required=True, type=bool)
        # Assist with luncheons, orientations or annual picnic
        self.postParser.add_argument('help_event', required=True, type=bool)
        # provide snacks/cookies/potluck dishes for special events
        self.postParser.add_argument('help_food', required=True, type=bool)

        # forth page
        self.postParser.add_argument('ref1_name', required=True)
        self.postParser.add_argument('ref2_name', required=True)
        self.postParser.add_argument('ref1_phone', required=True)
        self.postParser.add_argument('ref2_phone', required=True)
        self.postParser.add_argument('ref1_email', required=True)
        self.postParser.add_argument('ref2_email', required=True)

        self.postParser.add_argument('preferred_countries')
        self.postParser.add_argument('student_type')

        self.getParser = reqparse.RequestParser()
        self.getParser.add_argument('pending', type=bool, default=False)

    def post(self):
        user = auth_required()
        args = self.postParser.parse_args()

        update = {}
        copy_fields = ["first_name", "last_name", "email", "address",
                       "gender", "occupation", "phone",
                       "best_contact", "has_facebook", "add_facebook",
                       "hear_about_us", "household_size", "has_children",
                       "children_age", "has_pets", "pets", "smoker",
                       "help_board", "help_event", "help_food",
                       "preferred_countries"]

        if args["spouse_first_name"] or args["spouse_last_name"] or \
                args["spouse_occupation"]:
            update["spouse"] = {
                "first_name": args["spouse_first_name"],
                "last_name": args["spouse_last_name"],
                "occupation": args["spouse_occupation"]
            }
        for field in copy_fields:
            update[field] = args[field]

        update["preferred_gender"] = args["student_type"]
        update["references"] = [
            {
                "name": args["ref1_name"],
                "email": args["ref1_email"],
                "phone": args["ref1_phone"]
            }, {
                "name": args["ref2_name"],
                "email": args["ref2_email"],
                "phone": args["ref2_phone"]
            }
        ]
        try:
            uid = user.update_host_info(update)
        except Exception as e:
            return str(e), 500
        token = generate_token(3600 * 24 * 7, {
            "type": TokenType.HOST_VERIFICATION.value,
            "uid": user.uid
        })
        send_email(['internationalfriendstucson@gmail.com'],
                   'We Have a New Host!', 'emails/new_host',
                   values=update, token=token, uid=user.uid)
        return update

    def get(self):
        args = self.getParser.parse_args()
        user = role_required([Role.CO_CHAIR, Role.ADMIN])
        if args["pending"]:
            query = mongo.db.User.find({"phost_pending": True})
        else:
            query = mongo.db.User.find({"roles": {"$in": [Role.HOST]}})
        result = []
        for item in query:
            item["uid"] = str(item["_id"])
            del item["_id"]
            result.append(item)
        return item


def verify_host(uid):
    user = User(uid)
    if user.has_role(Role.HOST):
        return "The host is already verified: %s %s (%s)" %\
            (user.first_name, user.last_name, user.email)
    user.remove_role(Role.HOST_CANDIDATE)
    user.add_role(Role.HOST)
    user.update()
    
    send_email([user.email], 'Welcome Aboard!',
               'emails/out_host/verified', first_name=user.first_name)
    
    return "You have verify the host! An email has been sent to %s %s (%s)" %\
        (user.first_name, user.last_name, user.email)


class HostVerifyAPI(Resource):

    def get(self, uid):
        token = token_required(TokenType.HOST_VERIFICATION)
        return verify_host(token["uid"])
