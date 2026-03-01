from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import ValidationError
from typing import Optional
from jose import JWTError, jwt
from app.config import settings
from app.database import get_db
# In a real app we'd import the User model here. Using a placeholder or importing from models directly.
# from app.models.all_models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def get_current_user_token_payload(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception()
        return payload
    except JWTError:
        raise credentials_exception()

def credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

# async def get_current_user(payload: dict = Depends(get_current_user_token_payload), db: AsyncSession = Depends(get_db)):
#     """
#     In the real implementation this fetches the user from DB.
#     For multi-tenant saas, we return the user obj equipped with role and id.
#     """
#     pass
