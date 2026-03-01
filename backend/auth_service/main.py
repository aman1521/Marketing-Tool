"""
Auth Service - Handles all authentication and authorization
OAuth2 Integration, JWT token generation, session management
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from datetime import datetime, timedelta
import jwt
import os
import logging
from contextlib import asynccontextmanager
from typing import Optional, Dict, Any
import sys
import uuid
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models.database import DatabaseConfig, verify_database_setup
from shared.models.mongo import init_mongo, close_mongo
from shared.models.beanie_models import User as UserModel

from rbac import get_permissions_for_role, has_permission

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
SERVICE_NAME = "Auth Service"
API_VERSION = "0.1.0"
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24
REFRESH_TOKEN_EXPIRATION_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


# ============= Models =============
class TokenRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: int


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    password: str
    first_name: str
    last_name: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# ============= Utility Functions =============
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, email: str, role: str, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta is None:
        expires_delta = timedelta(hours=JWT_EXPIRATION_HOURS)
    
    expire = datetime.utcnow() + expires_delta
    
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def create_refresh_token(user_id: str) -> str:
    """Create refresh token"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRATION_DAYS)
    
    payload = {
        "user_id": user_id,
        "type": "refresh",
        "exp": expire
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Dict[str, Any]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ============= Lifespan =============
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {SERVICE_NAME} v{API_VERSION}")
    
    # Verify database connection
    db_status = verify_database_setup()
    if db_status["connection_successful"]:
        logger.info(f"✅ Database connected. Tables: {db_status.get('tables_count', 'unknown')}")
    else:
        logger.warning("⚠️ Database connection failed - service will start but database operations may fail")

    # Initialize MongoDB / Beanie
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017/aios_database")
    try:
        await init_mongo(mongo_url, [UserModel])
    except Exception as e:
        logger.warning(f"Failed to initialize MongoDB/Beanie: {e}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {SERVICE_NAME}")
    try:
        close_mongo()
    except Exception:
        pass
    DatabaseConfig.close()


# ============= FastAPI Application =============
app = FastAPI(
    title=SERVICE_NAME,
    description="Authentication and Authorization Service",
    version=API_VERSION,
    lifespan=lifespan
)


# ============= Routes =============
@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint with database status"""
    db_status = verify_database_setup()
    
    return {
        "status": "healthy" if db_status["connection_successful"] else "degraded",
        "service": SERVICE_NAME,
        "version": API_VERSION,
        "database": {
            "connected": db_status["connection_successful"],
            "tables_count": db_status.get("tables_count", 0)
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/auth/register", response_model=Dict[str, Any])
async def register(user: UserRegister) -> Dict[str, Any]:
    """
    Register new user
    """
    
    logger.info(f"Registration attempt for email: {user.email}")
    
    try:
        # Check if user already exists (by email)
        existing_user = await UserModel.find_one(UserModel.email == user.email)
        if existing_user:
            logger.warning(f"Registration failed: Email already registered - {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Check if username already exists
        existing_username = await UserModel.find_one(UserModel.username == user.username)
        if existing_username:
            logger.warning(f"Registration failed: Username already taken - {user.username}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )

        # Create new user (Beanie document)
        new_user = UserModel(
            email=user.email,
            username=user.username,
            password_hash=hash_password(user.password),
            first_name=user.first_name,
            last_name=user.last_name,
            role="business_owner"
        )

        await new_user.insert()

        logger.info(f"Registration successful: {user.email}")

        return {
            "success": True,
            "message": "User registered successfully",
            "user": {
                "id": str(new_user.id),
                "email": new_user.email,
                "username": new_user.username,
                "first_name": new_user.first_name,
                "last_name": new_user.last_name,
                "role": new_user.role
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@app.post("/api/v1/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin) -> TokenResponse:
    """
    Login user and return access token
    """
    
    logger.info(f"Login attempt for email: {credentials.email}")
    
    try:
        # Query user from MongoDB (Beanie)
        user = await UserModel.find_one(UserModel.email == credentials.email)

        if not user:
            logger.warning(f"Login failed: User not found - {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # Verify password
        if not verify_password(credentials.password, user.password_hash):
            logger.warning(f"Login failed: Invalid password - {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        if not user.is_active:
            logger.warning(f"Login failed: User inactive - {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive"
            )

        # Generate tokens
        access_token = create_access_token(str(user.id), user.email, user.role)
        refresh_token = create_refresh_token(str(user.id))

        logger.info(f"Login successful: {credentials.email}")

        expires_in = JWT_EXPIRATION_HOURS * 3600

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=expires_in
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@app.post("/api/v1/auth/refresh", response_model=TokenResponse)
async def refresh(credentials: HTTPAuthCredentials = Depends(security)) -> TokenResponse:
    """
    Refresh access token using refresh token
    """
    
    token = credentials.credentials
    payload = verify_token(token)

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user_id = payload.get("user_id")

    # Get user details from MongoDB
    try:
        user_obj = await UserModel.get(uuid.UUID(user_id))
    except Exception:
        user_obj = None

    if not user_obj:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found for refresh token"
        )

    email = user_obj.email
    role = user_obj.role

    new_access_token = create_access_token(user_id, email, role)
    new_refresh_token = create_refresh_token(user_id)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="Bearer",
        expires_in=JWT_EXPIRATION_HOURS * 3600
    )


@app.post("/api/v1/auth/verify", response_model=Dict[str, Any])
async def verify(credentials: HTTPAuthCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify JWT token validity
    """
    
    token = credentials.credentials
    payload = verify_token(token)
    role = payload.get("role", "business_owner")
    
    return {
        "valid": True,
        "user_id": payload.get("user_id"),
        "email": payload.get("email"),
        "role": role,
        "permissions": get_permissions_for_role(role)
    }

# ============= Permissions & Roles API =============
@app.get("/api/v1/auth/roles/permissions", response_model=Dict[str, Any])
async def get_role_permissions(credentials: HTTPAuthCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Returns available permissions for the current user's role
    """
    token = credentials.credentials
    payload = verify_token(token)
    role = payload.get("role", "business_owner")
    
    return {
        "role": role,
        "permissions": get_permissions_for_role(role)
    }


@app.post("/api/v1/auth/logout", response_model=Dict[str, Any])
async def logout(credentials: HTTPAuthCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Logout user - invalidate token
    
    In production, this would add the token to a blacklist
    """
    
    logger.info(f"Logout requested")
    
    # TODO: Add token to blacklist in Redis or database
    
    return {
        "success": True,
        "message": "Logged out successfully"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
