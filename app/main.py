# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import auth
from app.database import Base, engine

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Production Backend")

# ========================
# CORS Middleware
# ========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["https://yourdomain.com"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========================
# Routers
# ========================

app.include_router(auth.router)


@app.get("/")
def root():
    return {"status": "API Running"}
