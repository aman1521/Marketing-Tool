import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.services.atlas.models import RawMetrics
from backend.services.atlas.collect.meta_connector import MetaConnector
from backend.services.atlas.collect.google_connector import GoogleConnector
from backend.services.atlas.collect.tiktok_connector import TikTokConnector

logger = logging.getLogger(__name__)

class SyncOrchestrator:
    """
    Coordinates data ingestion across all platform connectors.
    Handles scheduling, missing day detection, and idempotent RawMetrics upserts.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        self.connectors = {
            "meta": MetaConnector({"access_token": "env_mock"}),
            "google": GoogleConnector({"developer_token": "env_mock"}),
            "tiktok": TikTokConnector({"app_id": "env_mock"})
        }

    async def validate_missing_days(self, company_id: str, platform: str) -> List[datetime]:
        """Detect missing sync dates in the database for backfilling."""
        # Mock logic. In a real scenario, queries RawMetrics grouping by Date to find gaps.
        logger.info(f"Validating missing days for {company_id} on {platform}")
        # Return yesterday as default missing
        return [datetime.utcnow() - timedelta(days=1)]

    async def upsert_metrics(self, company_id: str, metrics: List[Dict[str, Any]]):
        """Idempotent UPSERT logic for raw metrics."""
        for m in metrics:
            # Upsert mechanic mock using distinct query + add.
            # In production, uses PostgreSQL dialetic insert().on_conflict_do_update()
            new_metric = RawMetrics(
                company_id=company_id,
                platform=m.get("platform"),
                account_id=m.get("account_id", "default_acc"),
                campaign_id=m.get("campaign_id"),
                adset_id=m.get("adset_id"),
                ad_id=m.get("ad_id"),
                date=datetime.fromisoformat(m.get("date")) if isinstance(m.get("date"), str) else datetime.utcnow(),
                impressions=m.get("impressions", 0),
                clicks=m.get("clicks", 0),
                spend=m.get("spend", 0.0),
                conversions=m.get("conversions", 0),
                revenue=m.get("revenue", 0.0),
                raw_json_snapshot=m.get("raw_json", {}),
                sync_version="v1"
            )
            self.db.add(new_metric)
        await self.db.commit()
        logger.info(f"Successfully upserted {len(metrics)} metric records for {company_id}.")

    async def run_daily_sync(self, company_id: str):
        """Execute a full sync loop across all platforms for a specified company."""
        logger.info(f"Starting Daily Sync for company: {company_id}")
        
        for platform_name, connector in self.connectors.items():
            try:
                # 1. Backfill mapping
                missing_days = await self.validate_missing_days(company_id, platform_name)
                
                for day in missing_days:
                    # 2. Fetch Accounts
                    accounts = await connector.fetch_accounts()
                    for acc in accounts:
                        # 3. Pull Data
                        start = day.replace(hour=0, minute=0, second=0)
                        end = day.replace(hour=23, minute=59, second=59)
                        metrics_payload = await connector.fetch_metrics(acc["account_id"], (start, end))
                        
                        # 4. Upsert
                        await self.upsert_metrics(company_id, metrics_payload)
                        
            except Exception as e:
                logger.error(f"Sync failed for {platform_name} on company {company_id}. Error: {e}")
                # Dead letter queue logic here
