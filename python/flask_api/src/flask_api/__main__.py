from flask import Flask

from flask_api.blueprints.animals import bp_animal
from flask_api.database import db


def create_app() -> Flask:
    app = Flask(__name__)

    # https://github.com/pallets-eco/flask-sqlalchemy/blob/d099628055def6f94d11d407bbd1e80d96183cf9/src/flask_sqlalchemy/extension.py#L293
    # Set the config key used by `init_app`
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    db.init_app(app)

    app.register_blueprint(bp_animal)

    return app
