-- AI Growth Operating System - PostgreSQL Schema
-- Phase 1: Foundation Tables

-- 1. Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL CHECK (role IN ('business_owner', 'agency_admin', 'internal_operator')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 2. Businesses Table
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    business_type VARCHAR(50) NOT NULL,
    margin_percentage NUMERIC(5, 2),
    sales_cycle_days INTEGER,
    subscription_model BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 3. User-Business Relationship
CREATE TABLE user_business_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    role VARCHAR(50) NOT NULL CHECK (role IN ('owner', 'admin', 'operator')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, business_id)
);

-- 4. Platform Accounts
CREATE TABLE platform_accounts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    platform_name VARCHAR(50) NOT NULL CHECK (platform_name IN ('meta', 'google', 'tiktok', 'linkedin', 'shopify', 'woocommerce')),
    platform_account_id VARCHAR(255) NOT NULL,
    platform_token VARCHAR(1000),
    platform_token_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(business_id, platform_name, platform_account_id)
);

-- 5. Campaigns
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    platform_id UUID NOT NULL REFERENCES platform_accounts(id) ON DELETE CASCADE,
    campaign_name VARCHAR(255) NOT NULL,
    platform_campaign_id VARCHAR(255),
    campaign_objective VARCHAR(100),
    daily_budget NUMERIC(12, 2),
    campaign_status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Ad Sets
CREATE TABLE ad_sets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    platform_adset_id VARCHAR(255),
    adset_name VARCHAR(255),
    daily_budget NUMERIC(12, 2),
    audience_cluster_id UUID,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Creatives
CREATE TABLE creatives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    platform_creative_id VARCHAR(255),
    creative_type VARCHAR(50),
    format VARCHAR(50),
    hook_type VARCHAR(100),
    video_length_seconds INTEGER,
    body_copy TEXT,
    cta_text VARCHAR(255),
    creative_score NUMERIC(5, 2),
    predicted_ctr NUMERIC(5, 4),
    predicted_cvr NUMERIC(5, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 8. Campaign - Creative Relationship (Many-to-Many)
CREATE TABLE campaign_creatives (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    creative_id UUID NOT NULL REFERENCES creatives(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(campaign_id, creative_id)
);

-- 9. Audience Clusters
CREATE TABLE audience_clusters (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    cluster_name VARCHAR(255),
    cluster_number INTEGER,
    profitability_score NUMERIC(5, 2),
    scalability_score NUMERIC(5, 2),
    size INTEGER,
    demographics JSONB,
    interests JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. Performance Metrics
CREATE TABLE performance_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_id UUID NOT NULL REFERENCES platform_accounts(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    impressions BIGINT,
    clicks BIGINT,
    spend NUMERIC(12, 2),
    conversions INTEGER,
    revenue NUMERIC(12, 2),
    ctr NUMERIC(5, 4),
    cpc NUMERIC(8, 2),
    cvr NUMERIC(5, 4),
    roas NUMERIC(8, 4),
    watch_time_seconds BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform_id, campaign_id, metric_date)
);

-- 11. Budget Allocations (ML Output)
CREATE TABLE budget_allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    allocation_date DATE NOT NULL,
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    recommended_budget NUMERIC(12, 2),
    current_budget NUMERIC(12, 2),
    status VARCHAR(50) DEFAULT 'pending',
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 12. Strategy Outputs (LLM Generated)
CREATE TABLE strategy_outputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    generated_date DATE NOT NULL,
    content_calendar JSONB,
    funnel_structure JSONB,
    ad_copy_variations JSONB,
    hook_angles JSONB,
    budget_explanation TEXT,
    weekly_summary TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. ML Predictions Log
CREATE TABLE ml_predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    prediction_type VARCHAR(100),
    input_features JSONB,
    predicted_value NUMERIC(12, 4),
    actual_value NUMERIC(12, 4),
    error_rate NUMERIC(5, 4),
    prediction_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 14. Raw Data Logs (API Responses)
CREATE TABLE raw_data_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    platform_id UUID NOT NULL REFERENCES platform_accounts(id) ON DELETE CASCADE,
    data_type VARCHAR(100),
    raw_response JSONB,
    sync_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 15. Audit Logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    business_id UUID REFERENCES businesses(id),
    action VARCHAR(255),
    resource_type VARCHAR(100),
    resource_id UUID,
    before_state JSONB,
    after_state JSONB,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 16. API Error Tracking
CREATE TABLE api_errors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(100),
    method VARCHAR(50),
    endpoint VARCHAR(255),
    error_code VARCHAR(50),
    error_message TEXT,
    stacktrace TEXT,
    occurred_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Indexes for Performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_platform_accounts_business ON platform_accounts(business_id);
CREATE INDEX idx_campaigns_business ON campaigns(business_id);
CREATE INDEX idx_campaigns_platform ON campaigns(platform_id);
CREATE INDEX idx_ad_sets_campaign ON ad_sets(campaign_id);
CREATE INDEX idx_creatives_business ON creatives(business_id);
CREATE INDEX idx_performance_metrics_date ON performance_metrics(metric_date);
CREATE INDEX idx_performance_metrics_campaign ON performance_metrics(campaign_id);
CREATE INDEX idx_audience_clusters_business ON audience_clusters(business_id);
CREATE INDEX idx_ml_predictions_date ON ml_predictions(prediction_date);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_user_business_assignments_user ON user_business_assignments(user_id);
CREATE INDEX idx_user_business_assignments_business ON user_business_assignments(business_id);
