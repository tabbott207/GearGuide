from flask import Flask
from GearGuide.config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    from .models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from . import models

    # a simple page that fish
    @app.route('/fish')
    def fish():
        return '<><'
    
    # import and register frontend routes
    from .routes import bp as gearguide_bp
    app.register_blueprint(gearguide_bp)

    
    from .weather_route import bp as weather_bp
    app.register_blueprint(weather_bp)

    return app
