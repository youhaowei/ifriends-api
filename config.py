import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'Wildcat International Friends'
    MONGO_DBNAME = "IF"
    MONGO_USERNAME = 'youhaowei'
    MONGO_PASSWORD = '5C3Q4mFlZwjXbcQB'
    MONGO_HOST = os.environ.get(
        "MONGO_HOST") or 'ifriends-shard-00-02-ztz4d.mongodb.net'
    MONGO_PORT = os.environ.get("MONGO_PORT") or 27017

    @staticmethod
    def init_app(app):
        pass


class SandboxConfig(Config):
    DEBUG = True
    SERVER_NAME = os.environ.get("SERVER_NAME")


class DevelopmentConfig(Config):
    MONGO_URI = "mongodb://youhaowei:5C3Q4mFlZwjXbcQB@ifriends-shard-00-00-ztz4d.mongodb.net:27017,ifriends-shard-00-01-ztz4d.mongodb.net:27017,ifriends-shard-00-02-ztz4d.mongodb.net:27017/<DATABASE>?ssl=true&replicaSet=ifriends-shard-0&authSource=admin"
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
