from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import create_tables
from app.routes import auth, chat, coach, profile, recommendations, simulations

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="Financial AI SaaS",
    description="AI-powered personal finance advisor",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/web", StaticFiles(directory=WEB_DIR), name="web")

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/profile", tags=["Profile"])
app.include_router(recommendations.router, prefix="/recommendations", tags=["Recommendations"])
app.include_router(simulations.router, prefix="/simulations", tags=["Simulations"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(coach.router, prefix="/coach", tags=["Coach"])


@app.get("/")
async def root():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/manifest.webmanifest", include_in_schema=False)
async def manifest():
    return FileResponse(
        WEB_DIR / "manifest.webmanifest",
        media_type="application/manifest+json",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/service-worker.js", include_in_schema=False)
async def service_worker():
    return FileResponse(
        WEB_DIR / "service-worker.js",
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/offline", include_in_schema=False)
async def offline():
    return FileResponse(WEB_DIR / "offline.html")


@app.get("/favicon.svg", include_in_schema=False)
async def favicon():
    return FileResponse(WEB_DIR / "favicon.svg", media_type="image/svg+xml")


@app.get("/api")
async def api_root():
    return {"message": "Financial AI SaaS API", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
