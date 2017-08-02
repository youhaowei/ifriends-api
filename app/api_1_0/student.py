from flask_restful import reqparse, Resource
from ..decorators import token_required


class StudentsAPI(Resource):

    def __init__(self):
        self.postParser = reqparse.RequestParser()
        self.postParser.add_argument('first_name', required=True)
        self.postParser.add_argument('last_name', required=True)
        self.postParser.add_argument('spouse')
        self.postParser.add_argument("address", required=True)
        self.postParser.add_argument('dob', required=True)
        self.postParser.add_argument('gender', required=True)
        self.postParser.add_argument('zip', required=True, type=int)
        self.postParser.add_argument('city', required=True)
        self.postParser.add_argument('phone', required=True)
        self.postParser.add_argument('facebook', required=True)
        self.postParser.add_argument('major', required=True)
        self.postParser.add_argument('program', required=True)
        self.postParser.add_argument('graduate', required=True)
        self.postParser.add_argument('country')
        self.postParser.add_argument('homecity')
        self.postParser.add_argument('married')
        self.postParser.add_argument('relative')

    def post(self):
        user = token_required()
        args = self.postParser.parse_args()
        if len(args["aptnumber"]) == 0:
            args["full_address"] = args["address"]
        else:
            args["full_address"] = args["address"] + \
                " APT " + args["aptnumber"]
        user.update_student_info(args)
