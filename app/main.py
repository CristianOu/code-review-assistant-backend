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

# IP Whitelisting Middleware
ALLOWED_IPS = ["195.249.187.103"]  # Replace with your trusted IPs


@app.middleware("http")
async def restrict_ip_access(request: Request, call_next):
    client_ip = request.client.host
    print('client_ip', client_ip)

    if client_ip not in ALLOWED_IPS:
        raise HTTPException(
            status_code=403, detail="Access Denied: IP Not Allowed")

    response = await call_next(request)
    return response


@app.get("/")
async def read_root():
    return {"message": "Welcome to the AI Code Review Backend!"}
