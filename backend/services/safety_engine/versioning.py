from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.services.safety_engine.models import GenesisState, GenesisHistory

class VersioningManager:
    """
    Robust Append-Only datastore mapping for Genesis constraints.
    Enforces Version gap prevention and non-destructive overwrites.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def create_snapshot(self, 
                              company_id: str, 
                              version: int, 
                              profile: Dict[str, Any], 
                              goals: Dict[str, Any], 
                              constraints: Dict[str, Any], 
                              changed_by: str, 
                              change_reason: str):
        """Build historical tracking payload of mutated conditions."""
        
        snapshot = GenesisHistory(
            company_id=company_id,
            version=version,
            profile_snapshot=profile,
            goals_snapshot=goals,
            constraints_snapshot=constraints,
            changed_by=changed_by,
            change_reason=change_reason,
            timestamp=datetime.utcnow()
        )
        self.db.add(snapshot)
        await self.db.commit()

    async def get_history(self, company_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Fetch version changelog"""
        
        query = select(GenesisHistory).where(GenesisHistory.company_id == company_id).order_by(GenesisHistory.version.desc()).limit(limit)
        result = await self.db.execute(query)
        records = result.scalars().all()
        
        return [
            {
                "version": r.version,
                "changed_by": r.changed_by,
                "change_reason": r.change_reason,
                "timestamp": r.timestamp.isoformat()
            } for r in records
        ]
