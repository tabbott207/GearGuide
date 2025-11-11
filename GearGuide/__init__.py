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

    # a simple page that fish
    @app.route('/fish')
    def fish():
        return '<><'
    
    # import and register frontend routes
    from .routes import bp as gearguide_bp
    app.register_blueprint(gearguide_bp)

    return app
