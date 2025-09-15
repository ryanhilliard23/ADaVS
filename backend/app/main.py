from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.asset_routes import router as asset_router

app = FastAPI()

# Allow frontend to communicate with the backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(asset_router)

@app.get("/")
def root():
    return {"message": "FastAPI backend is running!"}

# Temporary test, will be removed later
@app.get("/test")
def test():
    return {"message": "Communication successful."}