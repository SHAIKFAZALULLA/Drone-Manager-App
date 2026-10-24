from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import APP_NAME, APP_VERSION, FRONTEND_ORIGINS
from backend.app.routes.resources import router as resources_router
from backend.app.routes.analytics import router as analytics_router
from backend.app.services.store import get_store

PROJECT_ROOT = Path(__file__).resolve().parents[2]
FRONTEND_DIR = PROJECT_ROOT / "frontend"

app = FastAPI(title=APP_NAME, version=APP_VERSION, description="Centralized Drone Fleet Management and Analytics System")
app.add_middleware(CORSMiddleware, allow_origins=FRONTEND_ORIGINS, allow_credentials=False, allow_methods=["*"], allow_headers=["*"])
app.include_router(resources_router)
app.include_router(analytics_router)

@app.get("/health", tags=["Health"])
def health():
    store = get_store()
    return {"status": "ok", "database_ready": store.ready, "database_error": store.error}

@app.get("/api/v1/config", tags=["Configuration"])
def frontend_config():
    return {"api_base_url": "/api/v1", "authentication_required": False, "database": "firestore"}


# Serve the dashboard and its assets from the same origin as the API.
# Register this mount after API routes so it cannot shadow API endpoints.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
