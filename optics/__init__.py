from platform import machine
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
#import config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    #app.config.from_object(config)
    app.config.from_envvar('APP_CONFIG_FILE')

    db.init_app(app)
    migrate.init_app(app, db)

    from . import models 

    from .views import main_views, information_views, user_views, static_views, trend_views, ctq_views, ncr_views, realTime_views, yield_views, auth_views, packing_views , machineLearning_views
    app.register_blueprint(main_views.bp)
    app.register_blueprint(information_views.bp)
    app.register_blueprint(user_views.bp)
    app.register_blueprint(static_views.bp)
    app.register_blueprint(trend_views.bp)
    app.register_blueprint(ctq_views.bp)
    app.register_blueprint(ncr_views.bp)
    app.register_blueprint(realTime_views.bp)
    app.register_blueprint(yield_views.bp)
    app.register_blueprint(auth_views.bp)
    app.register_blueprint(packing_views.bp)
    app.register_blueprint(machineLearning_views.bp)
    return app