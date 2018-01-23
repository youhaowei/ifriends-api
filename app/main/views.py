from . import main
from flask import flash, redirect, render_template, session, url_for, abort


@main.route("/")
def index():
    return render_template('index.html', html_id="home")
