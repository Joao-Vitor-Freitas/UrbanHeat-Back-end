import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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

# --- Configuração do CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # Permite requisições de qualquer origem (ideal para testar abrindo o index.html direto)
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos HTTP (GET, POST, etc)
    allow_headers=["*"],  # Permite todos os cabeçalhos
)
# ----------------------------

app.include_router(dashboard_router)
app.include_router(heatscore_router)
app.include_router(measurement_router)
app.include_router(region_router)
app.include_router(report_router)
app.include_router(sensor_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
