import { useState, useEffect } from 'react';
import { Bot, Target, AlertTriangle, Zap, CheckCircle2 } from 'lucide-react';
import '../App.css';

const MOCK_STRATEGY = {
    business_id: "biz_90210",
    deterministic_decision: {
        recommended_action: "scale_up_aggressively",
        suggested_budget: 1500,
        budget_scaling_factor: 1.25,
        should_replace_creative: true,
        platform_fit_score: 82.5,
        creative_replace_reason: "Fatigue threshold reached (High Frequency + Maturity)"
    },
    llm_strategy: `System Context: You are an autonomous AI Marketing Strategist operating via the AI Growth Operating System.

--- BUSINESS PROFILE ---
Client: Test Brand
Current Monthly Budget Capacity: $50000

--- BEHAVIOR & INTENT (Live Sourced) ---
Current Primary Cohort Intent: Ready to Buy
Intent Strength Score (0-1): 0.92

--- ML PREDICTIONS (Deterministic Output) ---
  > Expected ROAS: 3.1x (Confidence: 0.9)
  > Top Creative Score: 88/100

--- STRATEGIC OBJECTIVE ---
Based STRICTLY on the deterministic models above, formulate an updated 7-day budget execution strategy.

LLM Response:
Considering the highly intent-driven cohort ('Ready to Buy', 0.92 strength) and our expected 3.1x ROAS, I recommend immediately scaling the retargeting campaigns to capture demand. We will allocate the +25% daily scaling budget explicitly to bottom-of-funnel audiences.

Angles to pursue for replacement creatives:
1. Urgency/Scarcity: Highlight limited stock or expiring offers.
2. Hard Social Proof: Hero customer testimonials mirroring the demographic cluster.`,
    risk_flags: ["BUDGET_VELOCITY_HIGH"],
    timestamp: new Date().toISOString()
};

const StrategyEngine = () => {
    const [data, setData] = useState<typeof MOCK_STRATEGY | null>(null);

    useEffect(() => {
        const timer = setTimeout(() => {
            setData(MOCK_STRATEGY);
        }, 800);
        return () => clearTimeout(timer);
    }, []);

    if (!data) return (
        <div className="spinner-container">
            <div className="spinner"></div>
        </div>
    );

    return (
        <div className="page-content">
            <div className="header">
                <div>
                    <h1 className="page-title">Strategy Orchestrator</h1>
                    <p className="page-subtitle">Deterministic Rules + LLM Strategy Maps</p>
                </div>
                <span className="badge success">ORCHESTRATED</span>
            </div>

            <div className="grid strategy-grid">

                {/* ML / Rules Decision Card */}
                <div className="card glass-card">
                    <h2 className="card-title"><Target color="var(--primary)" size={22} /> Deterministic Engine</h2>
                    <div className="decision-stats">

                        <div className="decision-row">
                            <span className="decision-label">Action</span>
                            <span className="badge warning">{data.deterministic_decision.recommended_action}</span>
                        </div>

                        <div className="decision-row">
                            <span className="decision-label">Scale Factor</span>
                            <span className="decision-value">{(data.deterministic_decision.budget_scaling_factor * 100)}%</span>
                        </div>

                        <div className="decision-row">
                            <span className="decision-label">New Daily Budget</span>
                            <span className="decision-value text-success">${data.deterministic_decision.suggested_budget}</span>
                        </div>

                        <div className="decision-row">
                            <span className="decision-label">Platform Fit</span>
                            <span className="decision-value">{data.deterministic_decision.platform_fit_score}/100</span>
                        </div>

                    </div>

                    {data.deterministic_decision.should_replace_creative && (
                        <div className="alert-box alert-warning mt-4">
                            <AlertTriangle size={18} />
                            <div>
                                <strong>Replace Creative Required</strong>
                                <p>{data.deterministic_decision.creative_replace_reason}</p>
                            </div>
                        </div>
                    )}

                    {data.risk_flags.length > 0 && (
                        <div className="alert-box alert-danger mt-4">
                            <AlertTriangle size={18} />
                            <div>
                                <strong>Risk Flags Caught</strong>
                                <p>{data.risk_flags.join(", ")}</p>
                            </div>
                        </div>
                    )}

                </div>

                {/* LLM Strategy output */}
                <div className="card glass-card wide-card">
                    <h2 className="card-title"><Bot color="var(--accent-purple)" size={22} /> LLM Strategy Generation</h2>
                    <div className="llm-output-box">
                        <pre className="llm-text">{data.llm_strategy}</pre>
                    </div>
                    <div className="action-footer">
                        <button className="btn btn-primary">
                            <CheckCircle2 size={16} /> Push to Execution Pipeline
                        </button>
                        <button className="btn btn-secondary">
                            <Zap size={16} /> Regenerate
                        </button>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default StrategyEngine;
