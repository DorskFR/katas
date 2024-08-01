import json

import sqlalchemy
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from starlette_api.database.db_client import DatabaseClient


async def get_planets(request: Request) -> JSONResponse:
    db_client: DatabaseClient = request.app.state.db_client
    planets = await db_client.list_planets()
    return JSONResponse(planets, 200)


async def create_planet(request: Request) -> JSONResponse:
    db_client: DatabaseClient = request.app.state.db_client

    # Try to extract
    try:
        data = await request.json()
    except json.JSONDecodeError as error:
        raise HTTPException(400, "Invalid data") from error

    # Normally we would have validation.

    # Create
    try:
        created = await db_client.create_planet(data)
    except sqlalchemy.exc.IntegrityError as error:
        raise HTTPException(400, f"Could not save in database {error}") from error

    return JSONResponse(created, 201)


async def get_planet(request: Request) -> JSONResponse:
    db_client: DatabaseClient = request.app.state.db_client
    planet_id = request.path_params["planet_id"]

    planet = await db_client.get_planet(planet_id)
    if not planet:
        raise HTTPException(404, "Planet not found")

    return JSONResponse(planet, 200)


async def update_planet(request: Request) -> JSONResponse:
    db_client: DatabaseClient = request.app.state.db_client
    planet_id = request.path_params["planet_id"]
    data = await request.json()

    planet = await db_client.get_planet(planet_id)
    if not planet:
        raise HTTPException(404, "Planet not found")

    try:
        updated = await db_client.update_planet(planet_id, data)
    except sqlalchemy.exc.IntegrityError as error:
        raise HTTPException(400, "Could not save in database") from error

    return JSONResponse(updated, 200)


async def delete_planet(request: Request) -> JSONResponse:
    db_client: DatabaseClient = request.app.state.db_client
    planet_id = request.path_params["planet_id"]

    planet = await db_client.get_planet(planet_id)
    if not planet:
        raise HTTPException(404, "Planet not found")

    deleted = await db_client.delete_planet(planet_id)
    if not deleted:
        raise HTTPException(400, "Could not delete in database")

    return JSONResponse("OK", 200)


planets_routes = [
    Route("/", endpoint=get_planets, methods=["GET"]),
    Route("/", endpoint=create_planet, methods=["POST"]),
    Route("/{planet_id:int}", endpoint=get_planet, methods=["GET"]),
    Route("/{planet_id:int}", endpoint=update_planet, methods=["PATCH", "PUT", "POST"]),
    Route("/{planet_id:int}", endpoint=delete_planet, methods=["DELETE", "POST"]),
]
