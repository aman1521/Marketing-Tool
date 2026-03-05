import logging
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.services.execution.forge.models import ExperimentRegistryModel, ExperimentStatus

logger = logging.getLogger(__name__)

class ExperimentRegistry:
    """
    Manages the CRUD lifecycle of all sandbox experiments.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def register_experiment(self, experiment_data: Dict[str, Any]) -> str:
        """Create new experiment tracking object."""
        exp_id = f"exp_{experiment_data.get('company_id')}_{int(datetime.utcnow().timestamp())}"
        
        record = ExperimentRegistryModel(
            experiment_id=exp_id,
            company_id=experiment_data.get("company_id"),
            campaign_id=experiment_data.get("campaign_id"),
            hypothesis=experiment_data.get("hypothesis"),
            experiment_type=experiment_data.get("experiment_type"),
            variations_blob=experiment_data.get("variations"),
            sandbox_budget_allocated=experiment_data.get("sandbox_budget", 0.0),
            status=ExperimentStatus.RUNNING
        )
        
        self.db.add(record)
        await self.db.commit()
        logger.info(f"Forge registered new experiment: {exp_id}")
        return exp_id

    async def get_active_experiments(self, company_id: str) -> list[ExperimentRegistryModel]:
        """Fetch all currently running experiments for safety checks."""
        query = select(ExperimentRegistryModel).where(
            ExperimentRegistryModel.company_id == company_id,
            ExperimentRegistryModel.status == ExperimentStatus.RUNNING
        )
        res = await self.db.execute(query)
        return list(res.scalars().all())

    async def update_status(self, experiment_id: str, new_status: ExperimentStatus, stats: Optional[Dict[str, Any]] = None, winner: Optional[str] = None):
        """Update lifecycle state and optionally attach final statistical inference."""
        query = select(ExperimentRegistryModel).where(ExperimentRegistryModel.experiment_id == experiment_id)
        res = await self.db.execute(query)
        record = res.scalar_one_or_none()
        
        if not record:
            logger.error(f"Cannot update missing experiment: {experiment_id}")
            return
            
        record.status = new_status
        if new_status in [ExperimentStatus.COMPLETED, ExperimentStatus.KILLED, ExperimentStatus.PROMOTED]:
            record.end_time = datetime.utcnow()
            
        if stats:
            record.statistical_summary = stats
        if winner:
            record.winner_id = winner
            
        self.db.add(record)
        await self.db.commit()
        logger.info(f"Experiment {experiment_id} updated to {new_status.value}")
