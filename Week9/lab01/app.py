from flask import Flask

from blueprints.v1 import bp as v1_bp
from blueprints.v2 import bp as v2_bp


def create_app():
    app = Flask(__name__)
    app.register_blueprint(v1_bp, url_prefix="/api/v1")
    app.register_blueprint(v2_bp, url_prefix="/api/v2")
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)