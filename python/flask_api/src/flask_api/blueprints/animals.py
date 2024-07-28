import sqlalchemy
from flask import Blueprint, Response, abort, jsonify, request

from flask_api.database import db
from flask_api.models import Animal

bp_animal = Blueprint("animal", __name__, url_prefix="/animal")


# list
@bp_animal.route("/", methods=["GET"])
def get_animals() -> tuple[Response, int]:
    animals = db.session.execute(db.select(Animal).order_by(Animal.name)).scalars()
    return jsonify([animal.to_dict() for animal in animals]), 200


# create
@bp_animal.route("/", methods=["POST"])
def create_animal() -> tuple[Response, int]:
    # request.form.to_dict() gives everything in str there is no parsing done so bool would fail as "True"
    animal = Animal(
        **{k: v for k, v in request.form.items() if k != "is_predator"},
        is_predator=request.form["is_predator"].lower() in ["1", "true"],
    )
    db.session.add(animal)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        abort(400)
    return jsonify(animal.to_dict()), 201


# read
@bp_animal.route("/<int:animal_id>")
def get_animal(animal_id: int) -> tuple[Response, int]:
    # https://github.com/pallets-eco/flask-sqlalchemy/blob/d099628055def6f94d11d407bbd1e80d96183cf9/src/flask_sqlalchemy/extension.py#L741
    animal = db.get_or_404(Animal, animal_id)

    # https://github.com/pallets/flask/blob/a8956feba1e40105e7bc78fa62ce36c58d1c91e1/src/flask/json/__init__.py#L138
    return jsonify(animal.to_dict()), 200


# update
@bp_animal.route("/<int:animal_id>", methods=["PUT", "PATCH", "POST"])
def update_animal(animal_id: int) -> tuple[Response, int]:
    animal = db.get_or_404(Animal, animal_id)
    for attr in request.form:
        if hasattr(animal, attr):
            if attr == "is_predator":
                setattr(animal, attr, request.form[attr].lower() in ["1", "true"])
            else:
                setattr(animal, attr, request.form[attr])
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        abort(400)
    return jsonify(animal.to_dict()), 200


# delete
@bp_animal.route("/<int:animal_id>", methods=["DELETE", "POST"])
def delete_animal(animal_id: int) -> tuple[Response, int]:
    animal = db.get_or_404(Animal, animal_id)
    db.session.delete(animal)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        abort(400)
    return jsonify(animal.to_dict()), 200
