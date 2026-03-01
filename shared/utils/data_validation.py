from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ValidationError
import logging
import math

logger = logging.getLogger(__name__)

# ==========================================
# Phase 7.1 Data Governance Schema Enforcers
# ==========================================

class IncomingPerformanceSchema(BaseModel):
    """Strictly types and validates raw platform integrations."""
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    spend: float = Field(default=0.0, ge=0.0)
    conversions: int = Field(default=0, ge=0)
    revenue: float = Field(default=0.0, ge=0.0)
    
    # Optional fields that must be imputed if missing
    watch_time_seconds: Optional[int] = Field(default=None)

class DataGovernor:
    """
    Validates, imputes (fills missing data), and prepares raw analytics 
    to be safely ingested by Database and Machine Learning layers.
    """
    
    @staticmethod
    def enforce_and_impute(raw_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        1. Strips bad types.
        2. Imputes missing critical data using basic rules.
        """
        
        # Step 1: Pre-imputation mapping (e.g. Meta returns "spend" as string "$5.00")
        if isinstance(raw_payload.get('spend'), str):
            clean_spend = raw_payload['spend'].replace('$', '').replace(',', '')
            raw_payload['spend'] = float(clean_spend) if clean_spend else 0.0

        if isinstance(raw_payload.get('revenue'), str):
            clean_rev = raw_payload['revenue'].replace('$', '').replace(',', '')
            raw_payload['revenue'] = float(clean_rev) if clean_rev else 0.0
            
        try:
            # Step 2: Strict Pydantic parsing
            validated = IncomingPerformanceSchema(**raw_payload)
            clean_data = validated.dict()
            
            # Step 3: Impute missing derived metrics
            # If CTR/ROAS aren't explicitly passed, we calculate them directly to maintain perfect consistency
            clean_data['ctr'] = (clean_data['clicks'] / clean_data['impressions']) if clean_data['impressions'] > 0 else 0.0
            clean_data['cpc'] = (clean_data['spend'] / clean_data['clicks']) if clean_data['clicks'] > 0 else 0.0
            clean_data['cvr'] = (clean_data['conversions'] / clean_data['clicks']) if clean_data['clicks'] > 0 else 0.0
            clean_data['roas'] = (clean_data['revenue'] / clean_data['spend']) if clean_data['spend'] > 0 else 0.0
            
            # Step 4: Missing video stats heuristic
            if clean_data['watch_time_seconds'] is None:
                # Naive imputation assuming 3 seconds per impression for video feeds
                clean_data['watch_time_seconds'] = clean_data['impressions'] * 3

            return {
                "success": True,
                "data": clean_data
            }
            
        except ValidationError as e:
            logger.error(f"DATA GOVERNANCE SCHEMA FAILURE: {e.errors()}")
            return {
                "success": False,
                "error": e.errors(),
                "data": None
            }
