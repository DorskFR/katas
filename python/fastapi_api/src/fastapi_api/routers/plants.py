from typing import Any

import sqlalchemy
from fastapi import APIRouter, HTTPException
from sqlalchemy import delete, select

from fastapi_api.database import DBSessionDep
from fastapi_api.models import Plant, PlantCreate, PlantSchema, PlantUpdate

plant_router = APIRouter(prefix="/plants", tags=["plants"])


# list
@plant_router.get("", response_model=list[PlantSchema])
async def list_plants(session: DBSessionDep) -> Any:
    result = await session.scalars(select(Plant))
    return result.all()


# create
@plant_router.post("", response_model=PlantSchema)
async def create_plant(new_plant: PlantCreate, session: DBSessionDep) -> Any:
    plant = Plant(**new_plant.model_dump())
    session.add(plant)
    try:
        await session.commit()
    except sqlalchemy.exc.IntegrityError as error:
        raise HTTPException(400, "Could not save to database") from error
    return plant


# read
@plant_router.get("/{plant_id}", response_model=PlantSchema)
async def get_plant(plant_id: int, session: DBSessionDep) -> Any:
    result = await session.scalars(select(Plant).where(Plant.id == plant_id))
    if not (plant := result.first()):
        raise HTTPException(404, f"Plant id {plant_id} was not found")
    return plant


# update
@plant_router.patch("", response_model=PlantSchema)
async def update_plant(data: PlantUpdate, session: DBSessionDep) -> Any:
    result = await session.scalars(select(Plant).where(Plant.id == data.id))
    if not (plant := result.first()):
        raise HTTPException(404, f"Plant id {data.id} was not found")

    for key, value in data.model_dump(exclude_unset=True, exclude={"id"}).items():
        if hasattr(plant, key):
            setattr(plant, key, value)

    try:
        await session.commit()
    except sqlalchemy.exc.IntegrityError as error:
        raise HTTPException(400, "Could not save to database") from error
    await session.refresh(plant)
    return plant


# delete
@plant_router.delete("/{plant_id}", response_model=PlantSchema)
async def delete_plant(plant_id: int, session: DBSessionDep) -> Any:
    result = await session.scalars(select(Plant).where(Plant.id == plant_id))
    if not (plant := result.first()):
        raise HTTPException(404, f"Plant id {plant_id} was not found")
    await session.execute(delete(Plant).where(Plant.id == plant.id))
    await session.commit()
    return plant
