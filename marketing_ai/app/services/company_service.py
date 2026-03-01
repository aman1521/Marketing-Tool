from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.all_models import Company, User
from app.config import settings

class CompanyService:
    @staticmethod
    async def get_company_count(db: AsyncSession, user_id: str) -> int:
        statement = select(func.count(Company.id)).where(Company.owner_id == user_id)
        result = await db.execute(statement)
        return result.scalar()

    @staticmethod
    async def can_create_company(db: AsyncSession, user: User) -> bool:
        """
        Subscription Enforcement Logic
        Never trust frontend! Runs server-side.
        """
        # Role limit logic specified in requirements
        plan_limits = settings.PLAN_LIMITS
        
        current_count = await CompanyService.get_company_count(db, user.id)
        
        # Determine the user's role_type or fallback to limits
        allowed_limit = plan_limits.get(user.role_type, 1) # Default to 1 (business_owner) if somehow missing
        
        return current_count < allowed_limit

    @staticmethod
    async def create_company(db: AsyncSession, user: User, name: str, industry: str = None, target_audience: str = None) -> Company:
        if not await CompanyService.can_create_company(db, user):
            raise ValueError(f"Subscription Limit Exceeded: Your role '{user.role_type}' is limited to {settings.PLAN_LIMITS.get(user.role_type, 1)} companies.")
        
        new_company = Company(
            owner_id=user.id,
            name=name,
            industry=industry,
            target_audience=target_audience
        )
        db.add(new_company)
        await db.commit()
        await db.refresh(new_company)
        return new_company

    @staticmethod
    async def list_companies(db: AsyncSession, user: User) -> list[Company]:
        statement = select(Company).where(Company.owner_id == user.id)
        result = await db.execute(statement)
        return result.scalars().all()
