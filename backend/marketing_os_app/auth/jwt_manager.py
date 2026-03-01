import logging
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict

logger = logging.getLogger(__name__)

SECRET_KEY = "dummy_saas_secret_key_change_in_production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

class JWTManager:
    """
    Issues and decapsulates secure tokens encoding multi-tenant bounds permanently.
    """

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
            
        to_encode.update({"exp": expire})
        
        # Required bounds to process any OS Core action
        if "company_id" not in to_encode or "role" not in to_encode:
             raise ValueError("Cross-Tenant security violation: company_id/role missing from JWT generation.")
             
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[Dict[str, str]]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            client_id: str = payload.get("company_id")
            if client_id is None:
                return None
            return payload
        except jwt.PyJWTError:
            return None
