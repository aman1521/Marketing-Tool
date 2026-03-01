import urllib.parse
from app.config import settings
import httpx
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class OAuthService:
    """
    Handles generation of OAuth authorization URLs and exchanging authorization codes for Access Tokens.
    """
    
    # Define redirect URI which must match EXACTLY what is registered in Meta/Google consoles
    REDIRECT_URI = "http://localhost:8000/api/v1/connectors/oauth/callback"

    @staticmethod
    def get_authorization_url(platform: str, company_id: str) -> str:
        """
        Generates the login URL to redirect the user to Meta/Google.
        We pass the platform and company_id in the 'state' parameter to keep track of the session.
        """
        state_payload = f"{platform}::{company_id}"
        
        if platform == "meta":
            if not settings.META_APP_ID:
                raise ValueError("META_APP_ID is not configured.")
                
            base_url = "https://www.facebook.com/v19.0/dialog/oauth"
            params = {
                "client_id": settings.META_APP_ID,
                "redirect_uri": OAuthService.REDIRECT_URI,
                "state": state_payload,
                # Request permissions for Ads Management and Insights
                "scope": "ads_management,ads_read,business_management"
            }
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            return url
            
        elif platform == "google":
            if not settings.GOOGLE_CLIENT_ID:
                raise ValueError("GOOGLE_CLIENT_ID is not configured.")
                
            base_url = "https://accounts.google.com/o/oauth2/v2/auth"
            params = {
                "client_id": settings.GOOGLE_CLIENT_ID,
                "redirect_uri": OAuthService.REDIRECT_URI,
                "response_type": "code",
                "state": state_payload,
                "access_type": "offline",  # To get a refresh token
                "prompt": "consent",
                "scope": "https://www.googleapis.com/auth/adwords"
            }
            url = f"{base_url}?{urllib.parse.urlencode(params)}"
            return url
            
        else:
            raise ValueError(f"OAuth URL generation not supported for platform: {platform}")


    @staticmethod
    async def exchange_code_for_token(platform: str, code: str) -> dict:
        """
        Takes the authorization code provided by the OAuth redirect and exchanges it for the Long-lived Access Token.
        """
        async with httpx.AsyncClient() as client:
            if platform == "meta":
                 token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
                 params = {
                     "client_id": settings.META_APP_ID,
                     "redirect_uri": OAuthService.REDIRECT_URI,
                     "client_secret": settings.META_APP_SECRET,
                     "code": code
                 }
                 response = await client.get(token_url, params=params)
                 
                 if response.status_code != 200:
                     logger.error(f"Meta Token Exchange Failed: {response.text}")
                     raise HTTPException(status_code=400, detail="Failed to exchange Meta token.")
                     
                 # Contains access_token, token_type, and expires_in
                 return response.json()
                 
            elif platform == "google":
                 token_url = "https://oauth2.googleapis.com/token"
                 data = {
                     "code": code,
                     "client_id": settings.GOOGLE_CLIENT_ID,
                     "client_secret": settings.GOOGLE_CLIENT_SECRET, # Note: Requires backend env var to not be empty
                     "redirect_uri": OAuthService.REDIRECT_URI,
                     "grant_type": "authorization_code"
                 }
                 response = await client.post(token_url, data=data)
                 
                 if response.status_code != 200:
                     logger.error(f"Google Token Exchange Failed: {response.text}")
                     raise HTTPException(status_code=400, detail="Failed to exchange Google token.")
                     
                 # Contains access_token, refresh_token, token_type, expires_in
                 return response.json()
                 
            else:
                 raise ValueError("Unsupported platform for token exchange.")
