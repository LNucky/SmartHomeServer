import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routes import devices, scenario, sensors, update


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Запуск миграций при старте
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config("alembic.ini")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: command.upgrade(alembic_cfg, "head"))
    from db.seed_readings import seed_sensor_readings_if_empty

    await seed_sensor_readings_if_empty()
    yield


app = FastAPI(title="SmartHome API", lifespan=lifespan)

app.include_router(update.router, prefix="/api")
app.include_router(sensors.router, prefix="/api")
app.include_router(devices.router, prefix="/api")
app.include_router(scenario.router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "SmartHome API", "docs": "/docs"}
