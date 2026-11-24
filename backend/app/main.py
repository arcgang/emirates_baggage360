"""FastAPI application factory."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import auth
from .routers import operations
from .routers import partner
from .routers import passenger
from .routers import executive


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print("Starting Baggage360 Backend...")
    yield
    # Shutdown
    print("Shutting down Baggage360 Backend...")


app = FastAPI(
    title="Emirates Baggage360 API",
    version="1.0.0",
    description="Same-origin API for Emirates Baggage360 web-only demo",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
def health():
    """Liveness check."""
    return {"status": "ok"}

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(operations.router, prefix="/api/v1", tags=["Operations"])
app.include_router(partner.router, prefix="/api/v1", tags=["Partner"])
app.include_router(passenger.router, prefix="/api/v1", tags=["Passenger"])
app.include_router(executive.router, prefix="/api/v1", tags=["Executive"])
