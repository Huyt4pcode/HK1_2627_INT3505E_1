from flask import Flask
from .extensions import db, migrate
from .api.products import products_bp
from .errors import register_error_handlers
from .api.health import health_bp
from .config import DefaultConfig
import os

def create_app(config=None):
    app = Flask(__name__)
    cfg = config or os.environ.get("APP_CONFIG", DefaultConfig)
    app.config.from_object(cfg)
    
    db.init_app(app)
    migrate.init_app(app, db)
    
    app.register_blueprint(products_bp)
    app.register_blueprint(health_bp)
    register_error_handlers(app)
    
    return app