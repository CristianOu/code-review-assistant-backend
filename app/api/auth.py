from fastapi import APIRouter
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")

GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")




# Dummy router for authentication
router = APIRouter()

@router.get("/login")
def login():
  print('==== GITHUB_CLIENT_SECRET', GITHUB_CLIENT_SECRET)
  return {"message": "Auth login route works!"}