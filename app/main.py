# app/main.py
from fastapi import FastAPI
from app.api import auth, pr, analyze

app = FastAPI()

# Include API routes
app.include_router(auth.router, prefix="/auth")
app.include_router(pr.router, prefix="/pr")
app.include_router(analyze.router, prefix="/analyze")


@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Code Review Backend!"}
