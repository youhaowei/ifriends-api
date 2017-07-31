from flask import request
from . import auth

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        pass