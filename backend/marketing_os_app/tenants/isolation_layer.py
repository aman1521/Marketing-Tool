from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
import logging

from backend.marketing_os_app.models import TenantRegistryModel

logger = logging.getLogger(__name__)

class IsolationLayer:
    """
    Enforces that queries across any system component inject the `company_id` filter
    as the first and absolute WHERE clause across all core OS components.
    """
    
    @staticmethod
    async def get_tenant_by_company(db: AsyncSession, company_id: str) -> TenantRegistryModel:
        query = select(TenantRegistryModel).where(TenantRegistryModel.company_id == company_id)
        res = await db.execute(query)
        record = res.scalar_one_or_none()
        
        if not record:
             raise HTTPException(status_code=404, detail="Tenant context invalid.")
             
        return record

    @staticmethod
    def enforce_isolation(request_company_id: str, context_company_id: str):
        """
        Hard-stops execution if someone's JWT mismatches the payload they requested.
        """
        if request_company_id != context_company_id:
             logger.critical(f"MULTI-TENANT LEAK ATTEMPTED: JWT mapped to {context_company_id} requested {request_company_id}")
             raise HTTPException(status_code=403, detail="Cross-tenant access absolutely restricted.")
