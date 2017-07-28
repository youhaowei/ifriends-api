from flask import Flask
from flask_pymongo import PyMongo

from config import config
from flask_restful import Api

mongo = PyMongo()


def create_app(config_name):
    """Factory for Flask App"""
    app = Flask("__name__")
    app.config.from_object(config[config_name])
    mongo.init_app(app)

    # attach routes and custom error pages here
    from .main import main as main_blueprint
    from .api_1_0 import api_bp as api_1_0_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    return app
