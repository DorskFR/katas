from fastapi import FastAPI
from fastapi.responses import JSONResponse

from fastapi_api.routers.plants import plant_router

app = FastAPI()


@app.get("/")
async def root() -> JSONResponse:
    return JSONResponse({"message": "API v1"})


app.include_router(plant_router)
