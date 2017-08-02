from flask import request
from . import auth
from ..models.user import User


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            user = User.verify_password(email, password)
        except Exception as e:
            return str(e), 400
        return user.generate_token()
    else:
        return None
