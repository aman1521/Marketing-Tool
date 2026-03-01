from fastapi import APIRouter
router = APIRouter()

@router.post("/login")
async def login():
    return {"access_token": "mocked", "token_type": "bearer"}
    
@router.post("/register")
async def register():
    return {"id": "user_id_123", "email": "test@test.com"}
