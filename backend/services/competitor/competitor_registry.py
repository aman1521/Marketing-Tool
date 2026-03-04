"""
Competitor Registry
===================
CRUD layer for managing tracked competitor profiles per tenant.
"""

import uuid
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# In-memory registry (replace with DB queries via SQLAlchemy in production)
_registry: Dict[str, Dict[str, Any]] = {}


class CompetitorRegistry:
    """Tenant-scoped competitor management."""

    def register(self, company_id: str, name: str, domain: str,
                 industry: str = "unknown") -> Dict[str, Any]:
        """Register a new competitor for tracking."""
        domain = domain.rstrip("/").lower()
        profile = {
            "id":           str(uuid.uuid4()),
            "company_id":   company_id,
            "name":         name,
            "domain":       domain,
            "industry":     industry,
            "is_active":    True,
            "last_crawled": None,
            "crawl_count":  0,
            "created_at":   datetime.utcnow().isoformat()
        }
        _registry[f"{company_id}::{domain}"] = profile
        logger.info(f"Registered competitor [{name}] for company [{company_id}]")
        return profile

    def list_competitors(self, company_id: str) -> List[Dict[str, Any]]:
        return [v for k, v in _registry.items() if v["company_id"] == company_id and v["is_active"]]

    def get_by_domain(self, company_id: str, domain: str) -> Optional[Dict[str, Any]]:
        key = f"{company_id}::{domain.lower()}"
        return _registry.get(key)

    def mark_crawled(self, company_id: str, domain: str):
        key = f"{company_id}::{domain.lower()}"
        if key in _registry:
            _registry[key]["last_crawled"] = datetime.utcnow().isoformat()
            _registry[key]["crawl_count"] += 1

    def deactivate(self, company_id: str, domain: str):
        key = f"{company_id}::{domain.lower()}"
        if key in _registry:
            _registry[key]["is_active"] = False
            logger.info(f"Deactivated competitor [{domain}] for company [{company_id}]")
