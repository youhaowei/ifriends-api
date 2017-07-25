import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'Wildcat Metropia TrafficDB'
    MONGO_DBNAME = "Traffic"

    @staticmethod
    def init_app(app):
        pass


class SandboxConfig(Config):
    DEBUG = True
    MONGO_HOST = os.environ.get("MONGO_HOST")
    MONGO_PORT = os.environ.get("MONGO_PORT") or 27017
    SERVER_NAME = os.environ.get("SERVER_NAME")


class DevelopmentConfig(Config):
    DEBUG = True
    MONGO_URI = os.environ.get("MONGO_URL") or "localhost"


class TestingConfig(Config):
    TESTING = True
    MONGO_URI = os.environ.get("MONGO_URL") or "localhost"


class ProductionConfig(Config):
    SERVER_NAME = os.environ.get("SERVER_NAME")
    MONGO_HOST = os.environ.get("MONGO_HOST")
    MONGO_PORT = os.environ.get("MONGO_PORT") or 27017


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'sandbox': SandboxConfig,
    'default': DevelopmentConfig
}
