from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseConnector(ABC):
    """
    Abstract Base Class for all Platform Connectors.
    Every platform (Meta, Google, TikTok etc) uses the same interface.
    """
    
    def __init__(self, company_id: str, platform_name: str, credentials_payload: dict):
        self.company_id = company_id
        self.platform_name = platform_name
        self.credentials_payload = credentials_payload # e.g. Access token, refresh token, secret
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """
        Verify connection and validity of the token.
        """
        pass
    
    @abstractmethod
    async def fetch_accounts(self) -> list[Dict[str, Any]]:
        """
        Return the linked platform accounts (e.g. Ad accounts mapped to the User)
        """
        pass
    
    @abstractmethod
    async def fetch_metrics(self, account_id: str, date_start: str, date_end: str) -> list[Dict[str, Any]]:
        """
        Pull daily aggregated RAW metrics (campaign spend, impressions, roas, revenue)
        """
        pass
    
    @abstractmethod
    async def execute_action(self, action: Dict[str, Any]) -> bool:
        """
        Execute an automated action dynamically back onto the platform.
        e.g., {'type': 'budget_increase', 'campaign_id': '12345', 'value': 20.00}
        """
        pass
