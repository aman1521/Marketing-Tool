from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, List, Dict
from fastapi.responses import RedirectResponse

from app.database import get_db
from app.models.all_models import User, PlatformConnection, Company, PlatformAccount, Campaign, Post
from app.services.base_connector import BaseConnector

router = APIRouter()

# Example mock connector registry dependency
# In reality, this yields configured subclasses of BaseConnector (MetaConnector, etc.)
def get_platform_connector(platform: str) -> BaseConnector:
    # return MetaConnector(...) if platform == "meta" else ...
    class StubConnector(BaseConnector):
        def get_authorization_url(self): 
            # For local demonstration, bounce directly into our own callback!
            return f"http://localhost:8000/api/v1/connectors/{platform}/callback?code=mock_auth_code_from_{platform}"
        async def authenticate(self, code): return {"access_token": f"live_{platform}_access_{code}", "refresh": "123", "expires_in": 3600}
        async def fetch_accounts(self, token): return [{"id" : "1", "name": f"{platform} Ad Account"}]
        async def fetch_metrics(self, token, acc_id): return {}
        async def execute_action(self, token, action, payload): return {}
    
    return StubConnector("stub_id", "stub_sec", f"http://localhost:8000/connectors/{platform}/callback")

@router.get("/{platform}/login", summary="Initiate Platform OAuth Login")
async def connect_platform(platform: str, company_id: str):
    """
    Returns the OAuth Authorization URL for the requested platform (Meta, Google, Reddit, etc)
    and passes internal company ID in state token.
    """
    connector = get_platform_connector(platform)
    auth_url = connector.get_authorization_url()
    
    # Normally we attach ?state=base64(company_id)
    return {"authorization_url": f"{auth_url}&state={company_id}"}


@router.get("/{platform}/callback", summary="Receive OAuth Callback")
async def platform_callback(
    platform: str, 
    code: str = Query(...), 
    state: str = Query(...), 
    db: AsyncSession = Depends(get_db)
):
    """
    Exchanges auth_code for token, securely encrypts the access tokens via AES, 
    and links to the PlatformConnection constraint of the company.
    """
    company_id = state
    connector = get_platform_connector(platform)
    
    try:
        # 1. Exchange Code 
        token_data = await connector.authenticate(code)
        
        # 2. Encrypt Token
        encrypted_access = connector.encrypt_token(token_data.get("access_token", ""))
        encrypted_refresh = connector.encrypt_token(token_data.get("refresh", "")) # Fallbacks if refresh is non-standard
        
        # 0. Demo Environment: Ensure Company exists so PostgreSQL Foreign Key doesn't crash
        company_exists = await db.execute(select(Company).where(Company.id == company_id))
        if not company_exists.scalar_one_or_none():
            db.add(Company(id=company_id, name="Demo Environment", industry="SaaS"))
            await db.commit() # Commit right away to ensure existence 
            
        # 3. Store to DB (PlatformConnection)
        stmt = select(PlatformConnection).where(
            PlatformConnection.company_id == company_id, 
            PlatformConnection.platform_name == platform
        )
        result = await db.execute(stmt)
        existing_conn = result.scalar_one_or_none()
        
        if existing_conn:
            existing_conn.encrypted_credentials = encrypted_access
            existing_conn.status = "connected"
            conn_id = existing_conn.id
        else:
            new_conn = PlatformConnection(
                company_id=company_id, 
                platform_name=platform, 
                encrypted_credentials=encrypted_access,
                status="connected"
            )
            db.add(new_conn)
            await db.flush() # flush to get the ID for related models
            conn_id = new_conn.id
            
        # 4. DEMO: Inject realistic mock data for Accounts, Campaigns, Posts based on the platform type
        account_exists = await db.execute(select(PlatformAccount).where(PlatformAccount.connection_id == conn_id))
        if not account_exists.scalars().all():
            new_acc = PlatformAccount(connection_id=conn_id, account_id=f"acc_{platform}_123", account_name=f"{platform.capitalize()} Primary Account")
            db.add(new_acc)
            await db.flush()
            
            # Inject Mock Campaign
            db.add(Campaign(account_id=new_acc.id, name=f"Q3 Scaling {platform.capitalize()}", status="active", daily_budget=110.00, performance_metrics={"spend": 450.50, "cpc": 1.25}))
            db.add(Campaign(account_id=new_acc.id, name=f"Retargeting 30 Days", status="paused", daily_budget=20.00, performance_metrics={"spend": 60.00, "cpc": 0.85}))
            
            # Inject Mock Post
            db.add(Post(account_id=new_acc.id, content=f"We just launched our massive sale! Check our {platform.capitalize()} shop!", status="published", engagement_metrics={"likes": 1250, "shares": 300}))
            
        await db.commit()
        
        # Redirect back to Next.js Frontend explicitly!
        return RedirectResponse(url=f"http://localhost:3000/companies/{company_id}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth Handshake failed: {str(e)}")

@router.get("/{company_id}/platforms", summary="List Connected Platforms")
async def get_company_platforms(company_id: str, db: AsyncSession = Depends(get_db)):
    """Returns connected platforms statuses dynamically."""
    stmt = select(PlatformConnection).where(PlatformConnection.company_id == company_id)
    result = await db.execute(stmt)
    conns = result.scalars().all()
    
    connected_platforms = {c.platform_name: c for c in conns}
    
    # We always return the 6 supported states, marking them connected or pending.
    all_platforms = ["meta", "google", "tiktok", "linkedin", "twitter", "reddit"]
    output = []
    
    for p in all_platforms:
        if p in connected_platforms:
            output.append({
                "platform": p, 
                "status": connected_platforms[p].status, 
                "last_sync": connected_platforms[p].last_sync
            })
        else:
            output.append({"platform": p, "status": "disconnected", "last_sync": None})
            
    return output

@router.get("/{company_id}/platforms/{platform}/accounts", summary="List specific Platform Ad/Content Accounts")
async def get_platform_accounts(company_id: str, platform: str):
    """Calls token decryption -> fetch_accounts() dynamic route"""
    connector = get_platform_connector(platform)
    # db row logic required here...
    
    mock_decrypted_token = "valid_token"
    accounts = await connector.fetch_accounts(mock_decrypted_token)
    return accounts
