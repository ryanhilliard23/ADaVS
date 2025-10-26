from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from .models.base import Base, engine
from .routes import asset_routes, scan_routes, vulnerability_routes, user_routes

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    print("INFO:     Database started")
    yield
    engine.dispose()
    print("INFO:     Database has been shutdown")

app = FastAPI(title="ADaVS", lifespan=lifespan)

# Allow frontend to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan_routes.router, prefix="/api")
app.include_router(asset_routes.router, prefix="/api")
app.include_router(vulnerability_routes.router, prefix="/api")
app.include_router(user_routes.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}