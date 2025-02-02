from fastapi import APIRouter

# Dummy router for authentication
router = APIRouter()

@router.get("/pr")
async def login():
  return {"message": "PR route works!"}