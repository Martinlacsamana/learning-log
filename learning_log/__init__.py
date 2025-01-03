from flask import Flask
from .models import db
from .routes import bp
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    app.register_blueprint(bp)
    
    return app 