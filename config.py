import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'Wildcat International Friends'
    MONGO_PORT = os.environ.get("MONGO_PORT") or 27017
    MONGO_URI = "mongodb://youhaowei:5C3Q4mFlZwjXbcQB@" + \
        "ifriends-shard-00-02-ztz4d.mongodb.net:27017," + \
        "ifriends-shard-00-01-ztz4d.mongodb.net:27017," + \
        "ifriends-shard-00-00-ztz4d.mongodb.net:27017/" + \
        "IF?ssl=true&replicaSet=ifriends-shard-0&authSource=admin"
    MAIL_SENDER = "International Friends"
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'internationalfriendstucson@gmail.com'
    MAIL_PASSWORD = 'WorldFriends717'
    MAIL_SENDER = 'internationalfriendstucson@gmail.com'
    MAIL_SUBJECT_PREFIX = "[FROM International Friends]"

    @staticmethod
    def init_app(app):
        pass


class SandboxConfig(Config):
    DEBUG = True
    SERVER_NAME = os.environ.get("SERVER_NAME")


class DevelopmentConfig(Config):

    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    SERVER_NAME = os.environ.get("SERVER_NAME")


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'sandbox': SandboxConfig,
    'default': DevelopmentConfig
}
