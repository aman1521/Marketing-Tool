from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ConnectorSyncLogBase(BaseModel):
    id: str
    records_pulled: int
    error_message: Optional[str] = None
    sync_duration_seconds: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class PlatformConnectorBase(BaseModel):
    id: str
    platform: str # meta, reddit, google_my_business, search_console, etc.
    status: str # active, expired, failed, pending
    external_account_id: Optional[str] = None
    last_sync_at: Optional[datetime] = None
    
    recent_logs: List[ConnectorSyncLogBase] = []
    
    class Config:
        from_attributes = True

class ConnectPlatformRequest(BaseModel):
    platform: str
    auth_grant_code: str
