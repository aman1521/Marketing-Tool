# Intelligence Layer Architecture
## Converting Signals → Behavioral Intelligence → Strategic Decisions

**Status**: Phase 2 Specification Document  
**Last Updated**: February 22, 2026  
**Priority**: High - Core competitive advantage

---

## 📊 Overview: The Complete Signal-to-Strategy Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  Paid Signals          │  Organic Signals      │  Behavioral    │
│  (Platform APIs)       │  (Social Platforms)   │  (First-Party) │
│                        │                       │                │
│  • Impressions         │ • Post reach          │ • Page time    │
│  • Clicks              │ • Saves               │ • Scroll depth │
│  • CTR                 │ • Shares              │ • Add to cart  │
│  • CPC                 │ • Comments            │ • Checkout     │
│  • Conversions         │ • Watch time          │ • Session dur. │
│  • ROAS                │ • Retention curve     │ • Repeat visits│
│  • Audience breakdown  │ • Completion rate     │ • Purchase     │
│                        │ • Follower growth     │   freq.        │
│                        │ • Engagement rate     │                │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│    BEHAVIOR FEATURE ENGINEERING LAYER (CRITICAL)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  A) ENGAGEMENT ANALYZER                                           │
│     Raw: 70% watch retention, 12% saves, 5% shares              │
│     ↓ Feature Engineering ↓                                      │
│     • Emotional Resonance Score (calculated from saves/comments)│
│     • Information Value Score (retention + saves vs shares)      │
│     • Viral Potential Score (shares + comments normalized)       │
│     • Content Category Classification (format + engagement type) │
│                                                                   │
│  B) CONVERSION BEHAVIOR ANALYZER                                  │
│     Raw: Funnel metrics, cart abandonment, session data          │
│     ↓ Feature Engineering ↓                                      │
│     • Conversion Friction Score (abandon rate normalized)        │
│     • Funnel Drop Detection (which step has highest drop)        │
│     • Intent Strength Indicator (pages visited + time on page)   │
│     • Purchase Readiness Score                                   │
│                                                                   │
│  C) INTENT CLASSIFICATION ENGINE                                  │
│     Raw: Scroll depth, page visits, ad clicks, content type      │
│     ↓ Feature Engineering ↓                                      │
│     • Cold Curiosity (low engagement, high scroll variance)      │
│     • Problem Aware (consistent engagement, product research)    │
│     • Solution Aware (cart adds, high product page time)         │
│     • Ready to Buy (previous purchase, email opens)              │
│                                                                   │
│  OUTPUT: Behavioral Feature Vector                                │
│  [emotional_resonance, info_value, viral_potential, friction... │
│   ...intent_class, purchase_readiness, ...]                      │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│        AUDIENCE SEGMENTATION & CLASSIFICATION LAYER              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  • High LTV Segments (clustering on lifetime value indicators)   │
│  • Repeat Buyer Clusters (purchase frequency + recency)          │
│  • One-Time Buyer Clusters (single conversion, no repeat)        │
│  • Dormant Segments (previously active, no recent activity)      │
│  • Acquisition Candidates (engaged but never purchased)          │
│                                                                   │
│  Segmentation Basis:                                             │
│  - Behavioral features (from above)                              │
│  - Demographic + psychographic data                              │
│  - Purchase history & frequency                                  │
│  - Content affinity (which emotional triggers resonate)          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│     STRUCTURED INTELLIGENCE OBJECT CREATION (KEY STEP)           │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  {                                                                │
│    "business_context": {                                          │
│      "type": "ecommerce",                                        │
│      "margin": 0.40,                                             │
│      "sales_cycle_days": 3,                                      │
│      "subscription_model": false                                 │
│    },                                                            │
│                                                                   │
│    "audience_intelligence": {                                     │
│      "high_roas_segment": {                                      │
│        "demographics": "Women 24-32, Urban",                     │
│        "ltv": 185.50,                                            │
│        "repeat_rate": 0.35,                                      │
│        "emotional_triggers": ["Transformation", "Relatability"], │
│        "preferred_format": "Short-form UGC",                     │
│        "engagement_metrics": {                                    │
│          "watch_retention": 0.72,                                │
│          "save_rate": 0.12,                                      │
│          "share_rate": 0.05,                                     │
│          "comment_rate": 0.08                                    │
│        }                                                         │
│      }                                                           │
│    },                                                            │
│                                                                   │
│    "platform_fit": {                                              │
│      "instagram_fit": 0.82,                                      │
│      "tiktok_fit": 0.68,                                         │
│      "youtube_fit": 0.55                                         │
│    },                                                            │
│                                                                   │
│    "behavior_insights": {                                         │
│      "product_page_time": 187.5,    /* seconds */                │
│      "checkout_dropoff_rate": 0.42,                              │
│      "cart_add_rate": 0.18,                                      │
│      "intention_score": 0.68,                                    │
│      "friction_points": ["Checkout form complexity"]             │
│    },                                                            │
│                                                                   │
│    "content_performance": {                                       │
│      "top_hooks": [                                              │
│        "Before/after transformation",                            │
│        "User success story",                                     │
│        "Problem-solution format"                                 │
│      ]                                                           │
│    }                                                             │
│  }                                                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│         LLM STRATEGY GENERATION (With Structured Context)        │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  PROMPT TEMPLATE:                                                │
│  "You are a performance marketing strategist expert.             │
│                                                                   │
│   Business Model: {business_context}                            │
│   Current Performance: {performance_metrics}                    │
│   Audience Intelligence: {audience_intelligence}                │
│   Behavioral Insights: {behavior_insights}                      │
│   Platform Fit Analysis: {platform_fit}                         │
│                                                                   │
│   Generate:                                                      │
│   1. 30-day content plan (format, frequency, posting time)       │
│   2. 5 ad hooks based on emotional triggers                      │
│   3. Funnel optimization suggestions (fix friction points)       │
│   4. Budget allocation recommendation (platform split)           │
│   5. Audience expansion strategy                                 │
│   6. Creative testing framework                                  │
│                                                                   │
│   Return as structured JSON."                                   │
│                                                                   │
│  OUTPUT: Strategic Recommendations (JSON)                        │
│  ✅ Content Plan with emotional triggers                         │
│  ✅ Ad hook variations for testing                               │
│  ✅ Platform-specific optimization                               │
│  ✅ Budget allocation percentages                                │
│  ✅ Audience expansion guidelines                                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│        DECISION ENGINE (Deterministic Logic Layer)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Converts LLM recommendations into executable actions:           │
│                                                                   │
│  ✅ Budget Adjustments                                            │
│     • Calculate platform budget splits based on fit scores       │
│     • Adjust daily budgets based on current ROAS                 │
│     • Scale or pause underperforming segments                    │
│                                                                   │
│  ✅ Creative Testing                                              │
│     • Create ad variations from hook suggestions                 │
│     • Configure A/B test parameters (sample size, duration)      │
│     • Assign test variants to audience segments                  │
│                                                                   │
│  ✅ Audience Expansion                                            │
│     • Create lookalike audiences from high-LTV segment           │
│     • Test new demographic targets                               │
│     • Expand within platform native audiences                    │
│                                                                   │
│  ✅ Funnel Optimization                                           │
│     • Identify checkout friction (from behavior insights)        │
│     • Generate optimization suggestions                          │
│     • Create retargeting campaigns for abandoned carts           │
│                                                                   │
│  OUTPUT: Execution Task Queue                                    │
│  [                                                               │
│    {task: "adjust_budget", platform: "instagram", new_daily: 150},│
│    {task: "create_adset", audience: "lookalike_main", creatives: [...]},│
│    {task: "enable_retargeting", segment: "cart_abandoners"},     │
│    {task: "schedule_posts", platform: "tiktok", times: [...]},  │
│    ...                                                           │
│  ]                                                               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│             EXECUTION LAYER (Platform APIs)                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  • Meta API: Adjust campaign budgets, create ad sets             │
│  • Google Ads API: Create search campaigns, adjust bids          │
│  • TikTok API: Create ads, adjust targeting                      │
│  • Shopify API: Create retargeting rules, update inventory       │
│  • CRM API: Create audience lists, send email campaigns          │
│                                                                   │
│  All done automatically based on decision engine output          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│           FEEDBACK LOOP (Continuous Improvement)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  • Monitor execution results                                     │
│  • Compare predicted vs actual performance                       │
│  • Update audience segments & behavioral features                │
│  • Retrain model with new data                                   │
│  • Cycle back to Behavior Feature Engineering                    │
│                                                                   │
│  Frequency: Daily analysis, Weekly strategy update               │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🏗️ How This Maps to Microservices

### Phase 2 Services (Coming in Implementation)

| Service | Responsibility | Key Operations |
|---------|-----------------|-----------------|
| **Behavior Analyzer** | Feature engineering from raw signals | ContentEngagementAnalyzer, ConversionBehaviorAnalyzer, IntentClassifier |
| **Audience Segmentation** | Clustering, LTV analysis, segment definition | K-means clustering, RFM analysis, cohort definition |
| **Intelligence Aggregator** | Builds structured context objects | Combines all analyzers into JSON intelligence object |
| **ML Prediction Service** (Existing) | Predicts performance, identifies patterns | Enhanced with behavioral features |
| **Strategy Engine** | LLM-based recommendation generation | Calls OpenAI/Anthropic with structured context |
| **Decision Engine** (Existing) | Converts recommendations to actionable tasks | Executes deterministic logic |
| **Platform Connector** (Existing) | Implements tasks via platform APIs | Meta, Google, TikTok, Shopify |

---

## 🧠 Critical: The Feature Engineering Layer

### Why This Matters

❌ **Weak Approach**: Send raw ROAS number to LLM
- LLM: "Increase budget"
- Problem: Generic, no context, might fail

✅ **Proper Approach**: Engineer behavioral features
- Raw: 70% watch retention, 12% saves, 5% shares
- Feature: Emotional Resonance Score = 0.72 (high information, low viral)
- Context: "Audience values education over entertainment"
- LLM: "Create educational content, emphasize expertise in ads"
- Action: More specific, grounded in audience behavior

### Feature Engineering Rules

#### A) Engagement Features

```python
# Raw Signals
watch_retention = 0.70
save_rate = 0.12
share_rate = 0.05
comment_rate = 0.08

# Engineered Features
emotional_resonance = (save_rate + comment_rate) / 2  # 0.10
information_value = watch_retention - share_rate      # 0.65
viral_potential = (share_rate + comment_rate) * 10    # 0.13

# Interpretation Logic
if emotional_resonance > 0.12 and share_rate < 0.08:
    content_type = "Informational"
    strategy_hint = "Emphasize expertise, educational value"
    
if share_rate > 0.15 and comment_rate > 0.12:
    content_type = "Viral/Emotional"
    strategy_hint = "Strong emotional appeal, platform momentum"
```

#### B) Conversion Features

```python
# Raw Signals
add_to_cart_rate = 0.18
checkout_abandon_rate = 0.42
avg_product_page_time = 187.5  # seconds
session_duration = 245  # seconds

# Engineered Features
purchase_intent = add_to_cart_rate * (avg_product_page_time / session_duration)  # 0.138
conversion_friction = 1 - (1 - checkout_abandon_rate) * (add_to_cart_rate / 0.25)  # 0.584
product_interest_strength = min(avg_product_page_time / 180, 1.0)  # 1.04 → 1.0

# Friction Point Detection
if checkout_abandon_rate > 0.35:
    friction_point = "Checkout process too complex"
    optimization = "Simplify form, add trust signals"
    
if add_to_cart_rate < 0.15 and product_page_time > 200:
    friction_point = "High interest but low conviction"
    optimization = "Add social proof, testimonials, guarantees"
```

#### C) Intent Features

```python
# Raw Signals
scroll_depth = 0.85  # 0-1 scale
pages_visited = 3.2  # avg per session
time_on_site = 245   # seconds
add_to_cart = True
previous_purchaser = False

# Engineered Features
intent_class = "Solution Aware"  # Classification
intent_strength = (scroll_depth + min(pages_visited/5, 1.0)) / 2  # 0.68

# Mapping Logic
if intent_strength < 0.3:
    segment = "Cold Curiosity"
    strategy = "Brand awareness, top-of-funnel content"
    
elif intent_strength < 0.6:
    segment = "Problem Aware"
    strategy = "Problem validation, alternative comparison"
    
elif intent_strength < 0.85:
    segment = "Solution Aware"
    strategy = "Product benefits, social proof, overcome objections"
    
else:
    segment = "Ready to Buy"
    strategy = "Last-mile incentives, urgency, guarantees"
```

---

## 📊 Structured Intelligence Object Schema

```json
{
  "report_id": "uuid",
  "timestamp": "2026-02-22T14:32:00Z",
  "business_id": "uuid",
  
  "business_context": {
    "type": "ecommerce|saas|marketplace|service",
    "margin_percentage": 40.0,
    "sales_cycle_days": 3,
    "subscription_model": false,
    "avg_customer_ltv": 185.50
  },
  
  "audience_segments": [
    {
      "segment_id": "high_roas_segment",
      "name": "Women 24-32 Urban",
      "size_estimate": 2500,
      "ltv": 185.50,
      "repeat_purchase_rate": 0.35,
      
      "behavioral_features": {
        "emotional_resonance_score": 0.72,
        "information_value_score": 0.65,
        "viral_potential_score": 0.13,
        "intent_class": "Solution Aware",
        "intent_strength": 0.78,
        "purchase_friction_score": 0.42
      },
      
      "emotional_triggers": [
        "Transformation",
        "Relatability",
        "Self-improvement"
      ],
      
      "preferred_content_format": "Short-form UGC",
      "preferred_platforms": ["Instagram", "TikTok"],
      
      "engagement_metrics": {
        "watch_retention_avg": 0.72,
        "save_rate": 0.12,
        "share_rate": 0.05,
        "comment_rate": 0.08,
        "click_through_rate": 0.065
      },
      
      "conversion_metrics": {
        "conversion_rate": 0.038,
        "roas": 1.85,
        "avg_order_value": 135.50,
        "cart_add_rate": 0.18,
        "checkout_abandon_rate": 0.42
      }
    }
  ],
  
  "platform_fit_analysis": {
    "platforms": [
      {
        "name": "Instagram",
        "fit_score": 0.82,
        "audience_overlap_pct": 85,
        "content_resonance": "High",
        "conversion_potential": "High",
        "recommended_budget_pct": 40
      },
      {
        "name": "TikTok",
        "fit_score": 0.68,
        "audience_overlap_pct": 72,
        "content_resonance": "Medium",
        "conversion_potential": "Medium-High",
        "recommended_budget_pct": 35
      },
      {
        "name": "YouTube",
        "fit_score": 0.55,
        "audience_overlap_pct": 45,
        "content_resonance": "Medium",
        "conversion_potential": "Medium",
        "recommended_budget_pct": 20
      }
    ]
  },
  
  "performance_summary": {
    "total_spend_30d": 5000.00,
    "total_revenue_30d": 9250.00,
    "roas": 1.85,
    "avg_cpc": 0.45,
    "impressions": 45000,
    "clicks": 2925,
    "conversions": 111,
    "conversion_rate": 0.038
  },
  
  "friction_points": [
    {
      "point": "Checkout process complexity",
      "impact": "42% abandon rate at checkout",
      "severity": "High",
      "estimated_impact": "$1200 monthly lost revenue"
    },
    {
      "point": "Mobile checkout UX",
      "impact": "60% of abandoners on mobile",
      "severity": "High",
      "estimated_impact": "$720 monthly"
    },
    {
      "point": "Limited social proof",
      "impact": "Low conversion on new visitors",
      "severity": "Medium",
      "estimated_impact": "$450 monthly"
    }
  ],
  
  "content_performance": {
    "top_performing_hooks": [
      "Before/after transformation",
      "User success story",
      "Problem-solution format"
    ],
    "top_performing_format": "Short-form UGC",
    "top_performing_angles": [
      "Transformation story",
      "Relatable struggle",
      "Quick result demonstration"
    ]
  },
  
  "model_metrics": {
    "prediction_accuracy": 0.84,
    "last_retrain_date": "2026-02-19",
    "data_freshness": "12 hours",
    "confidence_level": "High"
  }
}
```

---

## 🚀 Implementation Roadmap

### Phase 2A: Behavior Feature Engineering (Weeks 1-2)

**Goal**: Build the analyzers that convert raw signals to behavioral features

Components:
- ✅ EngagementAnalyzer (emotional resonance, information value, viral potential)
- ✅ ConversionBehaviorAnalyzer (friction detection, intent strength)
- ✅ IntentClassifier (cold/problem/solution/ready to buy)
- ✅ FeatureVector assembly

### Phase 2B: Audience Segmentation (Weeks 2-3)

**Goal**: Cluster audiences and identify high-value segments

Components:
- ✅ LTV Calculator
- ✅ K-means clustering on behavioral features
- ✅ Segment profiling
- ✅ Repeat buyer vs one-time identification

### Phase 2C: Intelligence Aggregation (Week 4)

**Goal**: Build structured intelligence objects

Components:
- ✅ IntelligenceAggregator service
- ✅ Data validation
- ✅ Schema enforcement
- ✅ Caching of complex computations

### Phase 2D: LLM Integration (Week 4-5)

**Goal**: Connect to OpenAI/Anthropic with proper context

Components:
- ✅ PromptBuilder (creates structured prompts)
- ✅ PerspectiveEngine: LLM calls with retry logic
- ✅ ResponseParser (extract JSON recommendations)
- ✅ Cost tracking

### Phase 2E: Testing & Validation (Week 5-6)

**Goal**: Verify each component with real data

---

## 💡 Key Insights for Implementation

### 1. Raw Data ≠ Intelligence
- 70% watch retention is just a number
- Paired with 12% saves and 5% shares → informational content signal
- Combined with business margin 40% and sales cycle 3 days → specific strategy

### 2. Context is Everything
- ❌ "ROAS is 1.8, increase budget" (LLM guessing)
- ✅ "Emotional resonance high, viral low, friction at checkout, target problem-aware segment" (LLM reasoning)

### 3. Deterministic + AI Balance
- AI (LLM): Creative strategy generation, pattern recognition
- Deterministic (Decision Engine): Budget calculations, API calls, constraints enforcement
- Both together = powerful & reliable

### 4. Feature Engineering is the Moat
- Competitors with raw data: Weak generic strategies
- You with engineered features: Specific testable strategies from patterns

---

## 📁 Files That Will Be Created

```
backend/
├── behavior_analyzer_service/
│   ├── main.py                    # FastAPI service
│   ├── engagement_analyzer.py     # Content resonance logic
│   ├── conversion_analyzer.py     # Funnel friction detection
│   ├── intent_classifier.py       # Audience intent segmentation
│   └── feature_engineer.py        # Raw signal → features
│
├── audience_segmentation_service/
│   ├── main.py                    # FastAPI service
│   ├── ltv_calculator.py          # Lifetime value computation
│   ├── clustering_engine.py       # K-means clustering
│   └── segment_profiler.py        # Segment characteristics
│
├── intelligence_service/
│   ├── main.py                    # FastAPI service
│   ├── aggregator.py              # Builds structured intelligence
│   ├── validation.py              # Schema validation
│   └── schemas/
│       └── intelligence_schema.py  # TypedDict schema
│
├── strategy_engine_service/
│   ├── main.py                    # FastAPI service
│   ├── prompt_builder.py          # Structured prompt creation
│   ├── llm_client.py              # OpenAI/Anthropic integration
│   └── response_parser.py         # JSON extraction
│
└── shared/
    ├── models/
    │   └── intelligence_models.py  # Pydantic response models
    └── utils/
        └── feature_templates.py    # Feature calculation library
```

---

## ✨ Next Steps

1. **Read this document** - Understand the philosophy
2. **Review the database schema** - We have the data structure
3. **Start Phase 2A** - Build first behavior analyzer
4. **Test with sample data** - Verify feature engineering works
5. **Iterate quickly** - Get real signal feedback

---

## 🎯 Success Criteria

**Phase 2 Complete When:**
- ✅ Can ingest paid + organic + behavioral signals from all platforms
- ✅ Behavioral features generated with >80% data coverage
- ✅ Audience segments created (minimum 3 distinct clusters)
- ✅ Structured intelligence object builds in <30 seconds
- ✅ LLM generates strategic recommendations from context
- ✅ Decision engine executes tasks automatically
- ✅ Manual tests pass: Signal → Intelligence → Strategy → Execution

---

This is the Intelligence Layer specification. Ready to start Phase 2A implementation?
