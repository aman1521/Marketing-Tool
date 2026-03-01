import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from cryptography.fernet import Fernet

# Ensure you have ENCRYPTION_KEY set in your .env
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

class BaseConnector(ABC):
    """
    Abstract base class for all Platform OAuth Connectors (Meta, Google, TikTok, LinkedIn, Twitter, Reddit)
    """
    platform_name: str
    
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    @abstractmethod
    def get_authorization_url(self) -> str:
        """Return the OAuth login URL for the platform."""
        pass

    @abstractmethod
    async def authenticate(self, auth_code: str) -> Dict[str, Any]:
        """
        Exchange auth_code for access_token and refresh_token.
        Returns: 
            {"access_token": str, "refresh_token": Optional[str], "expires_in": int}
        """
        pass

    @abstractmethod
    async def fetch_accounts(self, access_token: str) -> List[Dict[str, Any]]:
        """Fetch Ad Accounts, Pages, or Profiles accessible by this token."""
        pass

    @abstractmethod
    async def fetch_metrics(self, access_token: str, account_id: str) -> Dict[str, Any]:
        """Fetch engagement/spend metrics for the given account."""
        pass

    @abstractmethod
    async def execute_action(self, access_token: str, action_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action on the platform.
        action_type can be: 'change_budget', 'pause_campaign', 'create_post', etc.
        """
        pass

    def encrypt_token(self, token: str) -> str:
        """Encrypts a string (e.g., access token) for safe DB storage."""
        if not token:
            return token
        return cipher_suite.encrypt(token.encode()).decode()
        
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypts a stored string from the DB."""
        if not encrypted_token:
            return encrypted_token
        return cipher_suite.decrypt(encrypted_token.encode()).decode()
