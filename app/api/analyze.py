from fastapi import APIRouter

# Dummy router for authentication
router = APIRouter()

@router.get("/analyze")
async def login():
  return {"message": "analyze route works!"}