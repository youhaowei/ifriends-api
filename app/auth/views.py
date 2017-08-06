from flask import request, jsonify
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
        return jsonify({
            "token": str(user.generate_token().decode("ascii")),
            "uid": str(user.uid),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name
        })
    else:
        return None
