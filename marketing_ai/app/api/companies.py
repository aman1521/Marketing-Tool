from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.database import get_db
# In a real app we'd fetch the actual User object
from app.dependencies import get_current_user_token_payload
from app.schemas.all_schemas import CompanyCreate, CompanyResponse
from app.services.company_service import CompanyService
from app.models.all_models import User

router = APIRouter()

# Mock Dependency for multi-tenant extraction
# In prod, get_current_user_token_payload would yield the DB User or we fetch it here
async def get_current_user(token_payload: dict = Depends(get_current_user_token_payload), db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    user_id = token_payload.get("sub")
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate, 
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    try:
        new_company = await CompanyService.create_company(
            db=db,
            user=user,
            name=company_data.name,
            industry=company_data.industry,
            target_audience=company_data.target_audience
        )
        return new_company
    except ValueError as e:
        # Catch our Role Limitation exception
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

@router.get("/", response_model=List[CompanyResponse])
async def list_companies(
    user: User = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    companies = await CompanyService.list_companies(db, user)
    return companies

@router.get("/{company_id}/{platform}/assets")
async def get_company_platform_assets(
    company_id: str, 
    platform: str, 
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import select
    from app.models.all_models import PlatformConnection, PlatformAccount, Campaign, Post
    
    # Locate connection
    stmt = select(PlatformConnection).where(
        PlatformConnection.company_id == company_id,
        PlatformConnection.platform_name == platform
    )
    result = await db.execute(stmt)
    conn = result.scalar_one_or_none()
    
    if not conn:
        return {"campaigns": [], "posts": []}
        
    # Locate accounts
    acc_stmt = select(PlatformAccount).where(PlatformAccount.connection_id == conn.id)
    acc_result = await db.execute(acc_stmt)
    accounts = acc_result.scalars().all()
    
    if not accounts:
        return {"campaigns": [], "posts": []}
        
    account_ids = [acc.id for acc in accounts]
    
    # Locate Campaigns
    camp_stmt = select(Campaign).where(Campaign.account_id.in_(account_ids))
    camp_result = await db.execute(camp_stmt)
    campaigns = camp_result.scalars().all()
    
    # Locate Posts
    post_stmt = select(Post).where(Post.account_id.in_(account_ids))
    post_result = await db.execute(post_stmt)
    posts = post_result.scalars().all()
    
    # Serialize securely
    return {
        "campaigns": [
            {
                "id": c.id, 
                "name": c.name, 
                "status": c.status, 
                "dailyBudget": c.daily_budget, 
                "performanceMetrics": c.performance_metrics or {"spend": 0, "cpc": 0},
                "isAutoManaged": c.is_auto_managed
            } for c in campaigns
        ],
        "posts": [
            {
                "id": p.id,
                "content": p.content,
                "status": p.status,
                "scheduledFor": p.scheduled_for,
                "engagementMetrics": p.engagement_metrics or {"likes": 0, "shares": 0}
            } for p in posts
        ]
    }
