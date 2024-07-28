from collections.abc import Iterator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from flask_api.__main__ import create_app
from flask_api.database import db
from flask_sqlalchemy import SQLAlchemy

# Generated with Sonnet 3.5 with some corrections on the fixtures


@pytest.fixture(name="app", autouse=True)
def fixture_app() -> Flask:
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return app


@pytest.fixture(name="client", autouse=True)
def fixture_client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture(autouse=True)
def init_db(app: Flask) -> Iterator[SQLAlchemy]:
    with app.app_context():
        db.create_all()
        yield db
        db.drop_all()


def test_create_animal(client: FlaskClient) -> None:
    response = client.post(
        "/animal/",
        data={
            "name": "Lion",
            "order": "Carnivora",
            "family": "Felidae",
            "genus": "Panthera",
            "species": "leo",
            "is_predator": True,
        },
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Lion"
    assert data["is_predator"] is True


def test_get_animal(client: FlaskClient) -> None:
    # First, create an animal
    client.post(
        "/animal/",
        data={
            "name": "Elephant",
            "order": "Proboscidea",
            "family": "Elephantidae",
            "genus": "Loxodonta",
            "species": "africana",
            "is_predator": False,
        },
    )

    # Now, retrieve the animal
    response = client.get("/animal/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Elephant"
    assert data["is_predator"] is False


def test_update_animal(client: FlaskClient) -> None:
    # First, create an animal
    client.post(
        "/animal/",
        data={
            "name": "Tiger",
            "order": "Carnivora",
            "family": "Felidae",
            "genus": "Panthera",
            "species": "tigris",
            "is_predator": True,
        },
    )

    # Now, update the animal
    response = client.put("/animal/1", data={"name": "Bengal Tiger", "species": "tigris tigris"})
    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Bengal Tiger"
    assert data["species"] == "tigris tigris"


def test_delete_animal(client: FlaskClient) -> None:
    # First, create an animal
    client.post(
        "/animal/",
        data={
            "name": "Giraffe",
            "order": "Artiodactyla",
            "family": "Giraffidae",
            "genus": "Giraffa",
            "species": "camelopardalis",
            "is_predator": False,
        },
    )

    # Now, delete the animal
    response = client.delete("/animal/1")
    assert response.status_code == 200

    # Try to get the deleted animal
    response = client.get("/animal/1")
    assert response.status_code == 404


def test_get_all_animals(client: FlaskClient) -> None:
    # Create multiple animals
    animals = [
        {
            "name": "Lion",
            "order": "Carnivora",
            "family": "Felidae",
            "genus": "Panthera",
            "species": "leo",
            "is_predator": True,
        },
        {
            "name": "Elephant",
            "order": "Proboscidea",
            "family": "Elephantidae",
            "genus": "Loxodonta",
            "species": "africana",
            "is_predator": False,
        },
        {
            "name": "Penguin",
            "order": "Sphenisciformes",
            "family": "Spheniscidae",
            "genus": "Aptenodytes",
            "species": "forsteri",
            "is_predator": True,
        },
    ]

    for animal in animals:
        client.post("/animal/", data=animal)

    # Get all animals
    response = client.get("/animal/")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3
    assert data[0]["name"] == "Elephant"
    assert data[1]["name"] == "Lion"
    assert data[2]["name"] == "Penguin"
