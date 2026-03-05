from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class SEOMetricMapBase(BaseModel):
    organic_traffic_vol: int
    top_ranking_keywords_json: str
    page_speed_index: int
    domain_authority: int

class BusinessAssetBase(BaseModel):
    id: str
    asset_type: str # ad_account, social_page, website_domain, gmb_location
    name: str # e.g. "Acme Corp US Branch Meta Account", "acme.com"
    external_id: Optional[str] = None
    
    seo_metrics: Optional[SEOMetricMapBase] = None
    
    class Config:
        from_attributes = True

class CompanyBase(BaseModel):
    id: str
    name: str
    domain: Optional[str] = None
    industry: str
    subscription_tier: str
    created_at: datetime
    
    assets: List[BusinessAssetBase] = []
    
    class Config:
        from_attributes = True

class CreateCompanyRequest(BaseModel):
    name: str
    domain: Optional[str] = None
    industry: str
