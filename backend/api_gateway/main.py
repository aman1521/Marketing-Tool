"""
API Gateway - Main entry point for all services
Handles routing, authentication, rate limiting, and logging
"""

from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
import logging
from datetime import datetime
import os
from typing import Dict, Any, Optional
import jwt
import sys
import httpx
import json
import hashlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.models.mongo import init_mongo, close_mongo
import shared.models.beanie_models as bm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_VERSION = "0.1.0"
SERVICE_NAME = "API Gateway"
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
RATE_LIMIT_REQUESTS = 1000
RATE_LIMIT_WINDOW_SECONDS = 3600
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8001")
BUSINESS_SERVICE_URL = os.getenv("BUSINESS_SERVICE_URL", "http://business_service:8002")
ATLAS_COLLECT_URL = os.getenv("ATLAS_COLLECT_URL", "http://atlas_collect:8003")
ML_SERVICE_URL = os.getenv("ML_SERVICE_URL", "http://ml_service:8004")
BEHAVIOR_ANALYZER_URL = os.getenv("BEHAVIOR_ANALYZER_URL", "http://behavior_analyzer_service:8009")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://analytics_service:8010")


# ============= Request/Response Models =============
class HealthCheckResponse:
    def __init__(self):
        self.status = "healthy"
        self.service = SERVICE_NAME
        self.version = API_VERSION
        self.timestamp = datetime.utcnow().isoformat()


# ============= Middleware & Dependencies =============
async def get_bearer_token(request: Request) -> Optional[str]:
    """Extract JWT token from Authorization header"""
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return None
    
    try:
        scheme, token = auth_header.split()
        if scheme.lower() != "bearer":
            return None
        return token
    except ValueError:
        return None


async def verify_jwt_token(token: Optional[str] = Depends(get_bearer_token)):
    """Verify JWT token validity"""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token"
        )
    
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


# ============= Rate Limiting =============
class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = {}
    
    def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed based on rate limit"""
        now = time.time()
        
        if identifier not in self.requests:
            self.requests[identifier] = []
        
        # Remove old requests outside the window
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if now - req_time < self.window_seconds
        ]
        
        if len(self.requests[identifier]) >= self.max_requests:
            return False
        
        self.requests[identifier].append(now)
        return True


rate_limiter = RateLimiter(RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW_SECONDS)


async def check_rate_limit(request: Request):
    """Rate limit check middleware"""
    client_ip = request.client.host if request.client else "unknown"
    
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests"
        )


# ============= Request/Response Logging =============
async def log_request_response(request: Request, call_next):
    """Log all requests and responses"""
    start_time = time.time()
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path} from {request.client.host if request.client else 'unknown'}")
    
    try:
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"← {request.method} {request.url.path} "
            f"Status: {response.status_code} "
            f"Time: {process_time:.3f}s"
        )
        
        response.headers["X-Process-Time"] = str(process_time)
        return response
    except Exception as e:
        logger.error(f"Error processing {request.method} {request.url.path}: {str(e)}")
        raise


# ============= Lifespan Events =============
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {SERVICE_NAME} v{API_VERSION}")

    # Initialize MongoDB/Beanie (shared models)
    mongo_url = os.getenv("MONGO_URL", "mongodb://mongo:27017/aios_database")
    try:
        await init_mongo(mongo_url, [bm.User, bm.Business, bm.PlatformAccount])
    except Exception as e:
        logger.warning(f"Failed to initialize MongoDB/Beanie: {e}")

    yield

    # Shutdown
    try:
        close_mongo()
    except Exception:
        pass
    logger.info(f"Shutting down {SERVICE_NAME}")


# ============= FastAPI Application =============
app = FastAPI(
    title=SERVICE_NAME,
    description="Central API Gateway for AI Growth Operating System",
    version=API_VERSION,
    lifespan=lifespan
)


# ============= CORS Configuration =============
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= Security Middleware =============
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_ORIGINS
)


# ============= Custom Middleware =============
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add X-Process-Time header to all responses"""
    await log_request_response(request, call_next)


# ============= Caching System =============
# Simulating a Redis connection for Phase 8 architecture
REDIS_MOCK_STORE = {}

def generate_cache_key(method: str, url: str) -> str:
    """Generate a stable hash for a given HTTP request"""
    raw_key = f"{method}:{url}"
    return hashlib.sha256(raw_key.encode('utf-8')).hexdigest()

# ============= Generic Proxy Function =============
async def proxy_request(request: Request, target_url: str):
    """Generic function to proxy requests with Redis caching (Phase 8)"""
    
    # 1. Cache Interception Layer (GET requests only)
    if request.method == "GET":
        cache_key = generate_cache_key(request.method, target_url)
        if cache_key in REDIS_MOCK_STORE:
            logger.info(f"⚡ CACHE HIT (Redis mock): {target_url}")
            cached_res = REDIS_MOCK_STORE[cache_key]
            return JSONResponse(
                status_code=200,
                content=cached_res,
                headers={"X-Cache": "HIT"}
            )
            
    body = await request.body()
    
    # Filter out headers that should not be forwarded
    headers = {k: v for k, v in request.headers.items() if k.lower() not in {"host", "content-length"}}
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                content=body,
                params=request.query_params
            )
            
            # Extract JSON content for caching operations
            res_content = response.json() if response.content else None
            
            # 2. Cache writing layer
            if request.method == "GET" and response.status_code == 200 and res_content:
                cache_key = generate_cache_key(request.method, target_url)
                REDIS_MOCK_STORE[cache_key] = res_content
                # In actual deployment, we pass `ex=300` for 5min TTL to strictly redis.set()
                logger.debug(f"Cache miss. Data written to cache for {target_url}")
            
            return JSONResponse(
                status_code=response.status_code,
                content=res_content,
                headers={"X-Cache": "MISS"}
            )
        except httpx.RequestError as e:
            logger.error(f"Proxy error to {target_url}: {str(e)}")
            raise HTTPException(status_code=503, detail=f"Service unavailable: {target_url.split('/')[2]}")


# ============= Routes =============
@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": SERVICE_NAME,
        "version": API_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/", tags=["Info"])
async def root() -> Dict[str, Any]:
    """API Gateway root endpoint"""
    return {
        "service": SERVICE_NAME,
        "version": API_VERSION,
        "message": "Welcome to AI Growth Operating System API Gateway",
        "documentation": "/docs",
        "health": "/health"
    }


# ============= Auth Service Routes (Proxy) =============
@app.post("/api/v1/auth/login", tags=["Auth"])
async def login(email: str, password: str):
    """
    Login endpoint - proxies to Auth Service
    """
    # TODO: Implement proxy to auth service
    return {
        "message": "Login endpoint - auth service implementation pending"
    }


@app.post("/api/v1/auth/register", tags=["Auth"])
async def register(email: str, password: str, username: str):
    """
    Register endpoint - proxies to Auth Service
    """
    # TODO: Implement proxy to auth service
    return {
        "message": "Register endpoint - auth service implementation pending"
    }


@app.post("/api/v1/auth/refresh", tags=["Auth"])
async def refresh_token(current_user: dict = Depends(verify_jwt_token)):
    """
    Refresh token endpoint - proxies to Auth Service
    """
    # TODO: Implement proxy to auth service
    return {
        "message": "Token refresh endpoint - auth service implementation pending"
    }


# ============= Business Service Routes (Proxy) =============
@app.get("/api/v1/businesses/{business_id}", tags=["Business"])
async def get_business(business_id: str, current_user: dict = Depends(verify_jwt_token)):
    """
    Get business details - proxies to Business Service
    """
    # TODO: Implement proxy to business service
    return {
        "message": f"Get business {business_id} - business service implementation pending"
    }


@app.post("/api/v1/businesses", tags=["Business"])
async def create_business(current_user: dict = Depends(verify_jwt_token)):
    """
    Create business - proxies to Business Service
    """
    # TODO: Implement proxy to business service
    return {
        "message": "Create business endpoint - business service implementation pending"
    }


# ============= Behavior Analysis Routes (Proxy) =============
@app.api_route("/api/v1/analyze/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Behavior Analysis"])
async def proxy_behavior_analysis(path: str, request: Request, current_user: dict = Depends(verify_jwt_token)):
    return await proxy_request(request, f"{BEHAVIOR_ANALYZER_URL}/api/v1/analyze/{path}")

@app.api_route("/api/v1/classify/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Behavior Analysis"])
async def proxy_intent_classification(path: str, request: Request, current_user: dict = Depends(verify_jwt_token)):
    return await proxy_request(request, f"{BEHAVIOR_ANALYZER_URL}/api/v1/classify/{path}")

@app.api_route("/api/v1/behavior/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Behavior Analysis"])
async def proxy_behavior_root(path: str, request: Request, current_user: dict = Depends(verify_jwt_token)):
    return await proxy_request(request, f"{BEHAVIOR_ANALYZER_URL}/api/v1/behavior/{path}")


# ============= Analytics Routes (Proxy) =============
@app.api_route("/api/v1/analytics/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Analytics"])
async def proxy_analytics(path: str, request: Request, current_user: dict = Depends(verify_jwt_token)):
    return await proxy_request(request, f"{ANALYTICS_SERVICE_URL}/api/v1/analytics/{path}")


# ============= Platform Integration Routes (Proxy) =============
@app.api_route("/api/v1/platforms/{path:path}", methods=["GET", "POST", "PUT", "DELETE"], tags=["Platform Integrations"])
async def proxy_platforms(path: str, request: Request, current_user: dict = Depends(verify_jwt_token)):
    return await proxy_request(request, f"{ATLAS_COLLECT_URL}/api/v1/platforms/{path}")


# ============= Error Handlers =============
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "status_code": exc.status_code,
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "status_code": 500,
                "message": "Internal server error",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
