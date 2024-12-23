from flask import Flask
from src.config import Config
from src.api.routes import register_routes


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    register_routes(app)

    return app
