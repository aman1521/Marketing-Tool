from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UnifiedAdBase(BaseModel):
    id: str
    name: str # The creative name
    status: str
    media_url: Optional[str] = None
    
    spend: float = 0.0
    impressions: int = 0
    clicks: int = 0
    conversions: int = 0
    cpa: float = 0.0
    roas: float = 0.0
    ctr: float = 0.0
    
    class Config:
        from_attributes = True

class UnifiedAdSetBase(BaseModel):
    id: str
    name: str # e.g. "r/marketing Subscribers" or "Lookalike 1%"
    targeting_json: str
    daily_budget: float
    status: str
    
    ads: List[UnifiedAdBase] = []
    
    class Config:
        from_attributes = True

class UnifiedCampaignBase(BaseModel):
    id: str
    platform: str # reddit, meta, google_ads
    name: str
    objective: str
    status: str
    daily_budget: float
    autonomous_scaling_enabled: bool
    
    ad_sets: List[UnifiedAdSetBase] = []
    
    class Config:
        from_attributes = True
