# app/main.py
from fastapi import FastAPI, Request, HTTPException
from app.api import auth, pr, analyze
from starlette.middleware.cors import CORSMiddleware

app = FastAPI()

# Include API routes
app.include_router(auth.router, prefix="/auth")
app.include_router(pr.router, prefix="/pr")
app.include_router(analyze.router, prefix="/analyze")

# CORS Configuration (Optional)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Code Review Backend!"}
