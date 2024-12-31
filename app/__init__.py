from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from app.database import db
from openai import OpenAI
import os

# initialize extensions
openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # initialize extensions
    db.init_app(app)

    # register blueprints
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    return app 