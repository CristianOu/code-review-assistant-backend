from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")


# Dummy router for authentication
router = APIRouter()

# 1️⃣ Initiate GitHub OAuth Login


@router.get("/login")
async def login():
    github_oauth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}&redirect_uri={
            GITHUB_REDIRECT_URI}&scope=repo&state=4605"
    )
    return RedirectResponse(github_oauth_url)


# 2️⃣ Handle OAuth Callback & Get Access Token
@router.get("/callback")
async def callback(code: str):
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, headers=headers, data=data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=400, detail="Failed to retrieve access token")

        access_token = response.json().get("access_token")

    if not access_token:
        raise HTTPException(status_code=400, detail="Invalid access token")

    return {"access_token": access_token}


# 3️⃣ Fetch Authenticated User Information (Optional)
@router.get("/user")
async def get_user_info(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/user", headers=headers)

    if response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Failed to fetch user info")

    return response.json()
