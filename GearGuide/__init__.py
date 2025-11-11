from flask import Flask
from GearGuide.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from GearGuide import models

    # from GearGuide.routes import main_bp
    # app.register_blueprint(main_bp)

    return app
