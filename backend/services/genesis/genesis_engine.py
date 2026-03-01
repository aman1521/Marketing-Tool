import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import json

from backend.services.genesis.models import GenesisState
from backend.services.genesis.profile import GenesisProfileManager
from backend.services.genesis.goals import GenesisGoalsManager
from backend.services.genesis.constraints import GenesisConstraintsManager
from backend.services.genesis.mapping import GenesisMapping
from backend.services.genesis.versioning import VersioningManager

logger = logging.getLogger(__name__)

class GenesisEngine:
    """
    Central Nervous System routing configuration validations, persisting safe structural schemas, 
    managing history and producing internal payloads for downstream systems.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.profile_mgr = GenesisProfileManager()
        self.goals_mgr = GenesisGoalsManager()
        self.constraints_mgr = GenesisConstraintsManager()
        self.mapper = GenesisMapping()
        self.versioning = VersioningManager(db_session)
        
    async def get_active_genesis(self, company_id: str) -> Optional[Dict[str, Any]]:
        """Returns the fully validated and mapped active state structure for a company."""
        
        query = select(GenesisState).where(GenesisState.company_id == company_id)
        result = await self.db.execute(query)
        record = result.scalar_one_or_none()
        
        if not record:
            return None
            
        validated_profile = self.profile_mgr.validate_profile(record.profile_data)
        mappings = self.mapper.generate_mapping(validated_profile)
        
        return {
            "company_id": record.company_id,
            "version": record.version,
            "profile": record.profile_data,
            "goals": record.goals_data,
            "constraints": record.constraints_data,
            "mappings": mappings,
            "last_updated": record.updated_at.isoformat()
        }

    async def _safe_update(self, 
                           company_id: str, 
                           target_component: str, 
                           validated_payload: Dict[str, Any], 
                           changed_by: str, 
                           change_reason: str) -> Dict[str, Any]:
        """
        Internal safe mutation loop. Extracts existing state, increments version natively, 
        creates appending snapshot logs and persists to GenesisState table strictly.
        """
        
        query = select(GenesisState).where(GenesisState.company_id == company_id)
        result = await self.db.execute(query)
        record = result.scalar_one_or_none()
        
        if not record:
            raise ValueError(f"No active Genesis initialized for company {company_id}")
            
        # Parse existing memory
        current_profile = record.profile_data
        current_goals = record.goals_data
        current_constraints = record.constraints_data
        
        # Determine mapping updates
        if target_component == "profile":
            current_profile = validated_payload
        elif target_component == "goals":
            current_goals = validated_payload
        elif target_component == "constraints":
            current_constraints = validated_payload
            
        # Increment version exactly
        new_version = record.version + 1
        
        # Persist memory mutations safely
        record.profile_data = current_profile
        record.goals_data = current_goals
        record.constraints_data = current_constraints
        record.version = new_version
        
        # Create unbreakable historical snapshot tracking
        await self.versioning.create_snapshot(
            company_id=company_id,
            version=new_version,
            profile=current_profile,
            goals=current_goals,
            constraints=current_constraints,
            changed_by=changed_by,
            change_reason=change_reason
        )
        
        self.db.add(record)
        await self.db.commit()
        
        logger.info(f"Genesis Engine safely mutated {company_id} {target_component} to version {new_version}.")
        
        # In full production we trigger AMQP emit ("genesis.updated") to Captain/Atlas 
        return await self.get_active_genesis(company_id)

    # ---------------------------- Public API Write Mutations ----------------------------

    async def update_profile(self, company_id: str, profile_payload: Dict[str, Any], change_reason: str, changed_by: str = "api_user") -> Dict[str, Any]:
        """Expose validated route to mutate underlying structural business definitions"""
        profile = self.profile_mgr.validate_profile(profile_payload)
        return await self._safe_update(company_id, "profile", profile.model_dump(), changed_by, change_reason)

    async def update_goals(self, company_id: str, goals_payload: Dict[str, Any], change_reason: str, changed_by: str = "api_user") -> Dict[str, Any]:
        """Expose validated target parameter changes scaling / constraints"""
        goals = self.goals_mgr.validate_goals(goals_payload)
        return await self._safe_update(company_id, "goals", goals.model_dump(), changed_by, change_reason)
        
    async def update_constraints(self, company_id: str, constraints_payload: Dict[str, Any], change_reason: str, changed_by: str = "api_user") -> Dict[str, Any]:
        """Modify hardcore action caps governing strategy module."""
        constraints = self.constraints_mgr.validate_constraints(constraints_payload)
        return await self._safe_update(company_id, "constraints", constraints.model_dump(), changed_by, change_reason)

    async def get_version_history(self, company_id: str) -> List[Dict[str, Any]]:
        return await self.versioning.get_history(company_id)

    async def initialize_genesis(self, company_id: str, profile: Dict[str, Any], goals: Dict[str, Any], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """First time payload creation"""
        # Strictly Validate Base Components
        p_val = self.profile_mgr.validate_profile(profile).model_dump()
        g_val = self.goals_mgr.validate_goals(goals).model_dump()
        c_val = self.constraints_mgr.validate_constraints(constraints).model_dump()
        
        record = GenesisState(
            company_id=company_id,
            version=1,
            profile_data=p_val,
            goals_data=g_val,
            constraints_data=c_val
        )
        
        self.db.add(record)
        await self.db.commit()
        
        await self.versioning.create_snapshot(company_id, 1, p_val, g_val, c_val, "system", "Initial Setup")
        
        logger.info(f"Genesis Engine initialized memory framework for {company_id}.")
        return await self.get_active_genesis(company_id)
