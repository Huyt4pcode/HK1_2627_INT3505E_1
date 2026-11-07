from flask import Flask

from .extensions import api, db
from .products import blp


app = Flask(__name__)
app.config.update(
    SQLALCHEMY_DATABASE_URI="sqlite:///code_first.db",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    API_TITLE="Code-First Product API",
    API_VERSION="v1",
    OPENAPI_VERSION="3.0.3",
    OPENAPI_URL_PREFIX="/docs",
    OPENAPI_SWAGGER_UI_PATH="/swagger-ui",
    OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
)

db.init_app(app)
api.init_app(app)
api.register_blueprint(blp)

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
