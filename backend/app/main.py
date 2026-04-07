"""
TrustLens AI — FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes.auth import router as auth_router
from app.routes.datasets import router as datasets_router
from app.routes.mlmodels import router as mlmodels_router
from app.routes.governance import router as governance_router
from app.routes.audits import router as audits_router
from app.routes.model_cards import router as model_cards_router

app = FastAPI(
    title="TrustLens AI",
    description="AI Governance and Audit Toolkit",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(datasets_router)
app.include_router(mlmodels_router)
app.include_router(governance_router)
app.include_router(audits_router)
app.include_router(model_cards_router)


@app.get("/health")
def health():
    """Simple liveness probe."""
    return {"status": "ok", "app": settings.APP_NAME}
