from flask_restful import reqparse, Resource
from ..decorators import token_required


class HostsAPI(Resource):

    def __init__(self):
        self.postParser = reqparse.RequestParser()
        self.postParser.add_argument('first_name', required=True)
        self.postParser.add_argument('last_name', required=True)
        self.postParser.add_argument('spouse_name')
        self.postParser.add_argument("address", required=True)
        self.postParser.add_argument('aptnumber', required=True)
        self.postParser.add_argument('gender', required=True)
        self.postParser.add_argument('zip', required=True, type=int)
        self.postParser.add_argument('city', required=True)
        self.postParser.add_argument('phone', required=True)
        self.postParser.add_argument('facebook', required=True)
        self.postParser.add_argument('hear_aboutus', required=True)
        self.postParser.add_argument('household', required=True)
        self.postParser.add_argument('activity', required=True)
        self.postParser.add_argument('children')
        self.postParser.add_argument('pets')
        self.postParser.add_argument('child_ages')
        self.postParser.add_argument('number_of_pets')
        self.postParser.add_argument('smoker', type=bool)
        self.postParser.add_argument('ref1_name')
        self.postParser.add_argument('ref2_name')
        self.postParser.add_argument('ref1_phone')
        self.postParser.add_argument('ref2_phone')
        self.postParser.add_argument('ref1_email')
        self.postParser.add_argument('ref2_email')

    def post(self):
        user = token_required()
        args = self.postParser.parse_args()
        if len(args["aptnumber"]) == 0:
            args["full_address"] = args["address"]
        else:
            args["full_address"] = args["address"] + \
                " APT " + args["aptnumber"]
        user.update_host_info(args)
