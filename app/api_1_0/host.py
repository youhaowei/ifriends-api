from flask_restful import reqparse, Resource
from ..decorators import token_required


class HostsAPI(Resource):

    def __init__(self):

        """ first page """
        self.postParser = reqparse.RequestParser()
        self.postParser.add_argument('first_name', required=True)
        self.postParser.add_argument('last_name', required=True)
        self.postParser.add_argument('spouse_name')
        self.postParser.add_argument("occupation", required=True)
        self.postParser.add_argument("spouse_occupation")
        self.postParser.add_argument("address", required=True)
        self.postParser.add_argument('phone', required=True)
        self.postParser.add_argument('facebook', required=True, type=bool)
        self.postParser.add_argument('hear_aboutus', required=True)

        """ econd page """
        self.postParser.add_argument('household_size', required=True, type=int)
        self.postParser.add_argument('has_children', required=True, type=bool)
        self.postParser.add_argument('children_age')
        self.postParser.add_argument('pets')
        self.postParser.add_argument('smoker', required=True, type=bool)

        """ third page """
        # Serve on the International Friends Board or a Comittee
        self.postParser.add_argument('help_board', required=True)    
        # Assist with luncheons, orientations or annual picnic
        self.postParser.add_argument('help_event', required=True)
        # provide snacks/cookies/potluck dishes for special events
        self.postParser.add_argument('help_food', required=True)
        
        # forth page
        self.postParser.add_argument('ref1_name', required=True)
        self.postParser.add_argument('ref2_name', required=True)
        self.postParser.add_argument('ref1_phone', required=True)
        self.postParser.add_argument('ref2_phone', required=True)
        self.postParser.add_argument('ref1_email', required=True)
        self.postParser.add_argument('ref2_email', required=True)

        """ unpaged """
        self.postParser.add_argument('gender', required=True)  
        self.postParser.add_argument('activity', required=True)

    def post(self):
        user = token_required()
        args = self.postParser.parse_args()
        if len(args["aptnumber"]) == 0:
            args["full_address"] = args["address"]
        else:
            args["full_address"] = args["address"] + \
                " APT " + args["aptnumber"]
        user.update_host_info(args)
