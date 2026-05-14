from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import close_mongo_connection, connect_to_mongo
from app.routes.auth import router as auth_router
from app.routes.iot import router as iot_router
from app.routes.prediction import router as prediction_router
from app.routes.report import router as report_router
from app.routes.reports import router as reports_router
from app.routes.weather import router as weather_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(weather_router)
app.include_router(prediction_router)
app.include_router(iot_router)
app.include_router(report_router)
app.include_router(reports_router)

uploads_dir = Path(__file__).resolve().parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/")
async def root():
    return {"message": "Sanjeevani backend is running"}
