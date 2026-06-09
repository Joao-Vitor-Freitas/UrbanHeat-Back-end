import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from database.schema import create_tables

from controllers.dashboard_controller import router as dashboard_router
from controllers.heatscore_controller import router as heatscore_router
from controllers.measurement_controller import router as measurement_router
from controllers.region_controller import router as region_router
from controllers.report_controller import router as report_router
from controllers.sensor_controller import router as sensor_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    print("Banco de dados inicializado com sucesso.")

    print("Leitura do Arduino desativada para ambiente local.")

    yield


app = FastAPI(title="UrbanHeat API", lifespan=lifespan)

app.include_router(dashboard_router)
app.include_router(heatscore_router)
app.include_router(measurement_router)
app.include_router(region_router)
app.include_router(report_router)
app.include_router(sensor_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
