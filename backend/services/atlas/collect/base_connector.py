from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
from datetime import datetime

class BaseConnector(ABC):
    """
    Abstract Base Class for all Platform Connectors in Atlas Collect.
    Validates idempotent behaviors, standardizes async fetching, and supports retry mechanics.
    """
    
    def __init__(self, credentials: Dict[str, Any]):
        self.credentials = credentials
        self.connected = False

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the given platform using OAuth or access tokens."""
        pass

    @abstractmethod
    async def refresh_token(self) -> str:
        """Handle token refresh lifecycle natively to avoid sync failures."""
        pass

    @abstractmethod
    async def fetch_accounts(self) -> List[Dict[str, Any]]:
        """Retrieve accessible ad accounts."""
        pass

    @abstractmethod
    async def fetch_campaigns(self, account_id: str) -> List[Dict[str, Any]]:
        """Retrieve active and historical campaigns for indexing."""
        pass

    @abstractmethod
    async def fetch_metrics(self, account_id: str, date_range: Tuple[datetime, datetime]) -> List[Dict[str, Any]]:
        """Retrieve granular metrics for campaigns and adsets across the specified date range."""
        pass
