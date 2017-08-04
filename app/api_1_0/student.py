from flask_restful import reqparse, Resource
from ..helpers import token_required, auth_required


class StudentsAPI(Resource):

    def __init__(self):
        self.postParser = reqparse.RequestParser()
        self.postParser.add_argument('first_name', required=True)
        self.postParser.add_argument('last_name', required=True)
        self.postParser.add_argument('email', required=True)
        self.postParser.add_argument('dob', required=True)
        self.postParser.add_argument('spouse')
        self.postParser.add_argument("address", required=True)
        self.postParser.add_argument('phone', required=True)
        self.postParser.add_argument('country')
        self.postParser.add_argument('homecity')
        self.postParser.add_argument('has_relative', type=bool)
        self.postParser.add_argument('gender', required=True)

        self.postParser.add_argument('major', required=True)
        self.postParser.add_argument('program', required=True)
        self.postParser.add_argument('duration', required=True)

        self.postParser.add_argument('like_hiking', type=bool)
        self.postParser.add_argument('like_music', type=bool)
        self.postParser.add_argument('like_music', type=bool)
        self.postParser.add_argument('like_movies', type=bool)
        self.postParser.add_argument('like_sports', type=bool)
        self.postParser.add_argument('like_reading', type=bool)
        self.postParser.add_argument('like_cooking', type=bool)
        self.postParser.add_argument('like_arts', type=bool)
        self.postParser.add_argument('other_interest')

        self.postParser.add_argument('host_preference')
        self.postParser.add_argument('has_car', type=bool)
        self.postParser.add_argument('dietary')
        self.postParser.add_argument('allergies')

    def post(self):
        user = auth_required()
        args = self.postParser.parse_args()
        ua_email = '@email.arizona.edu'
        if args["email"][-len(ua_email):] != ua_email:
            abort(403, "Not a valid U of A email address.") 
        user.update_student_info(args)
        return args
