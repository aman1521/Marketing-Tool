from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class RawMetrics(Base):
    __tablename__ = 'raw_metrics'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    platform = Column(String, index=True, nullable=False)
    account_id = Column(String, nullable=False)
    campaign_id = Column(String, index=True, nullable=False)
    adset_id = Column(String)
    ad_id = Column(String)
    date = Column(DateTime, index=True, nullable=False)
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    spend = Column(Float, default=0.0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    raw_json_snapshot = Column(JSON)
    sync_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class EngineeredFeatures(Base):
    __tablename__ = 'engineered_features'
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(String, index=True, nullable=False)
    campaign_id = Column(String, index=True, nullable=False)
    feature_version = Column(String, nullable=False)
    feature_blob = Column(JSON, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)

class EventLog(Base):
    __tablename__ = 'event_log'
    id = Column(Integer, primary_key=True, autoincrement=True)
    engine_name = Column(String, index=True, nullable=False)
    engine_version = Column(String, nullable=False)
    input_hash = Column(String, nullable=False)
    output_blob = Column(JSON)
    confidence_score = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    outcome_label = Column(String)

class BenchmarkSnapshots(Base):
    __tablename__ = 'benchmark_snapshots'
    id = Column(Integer, primary_key=True, autoincrement=True)
    industry = Column(String, index=True, nullable=False)
    aov_range = Column(String, index=True, nullable=False)
    metric_name = Column(String, nullable=False)
    percentile_25 = Column(Float)
    percentile_50 = Column(Float)
    percentile_75 = Column(Float)
    calculated_at = Column(DateTime, default=datetime.utcnow)
