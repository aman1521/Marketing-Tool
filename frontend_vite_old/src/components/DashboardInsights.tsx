import { useState, useEffect } from 'react';
import '../App.css';

// Mock data based on the API response structure
const MOCK_DATA = {
    engagement: {
        features: {
            emotional_resonance: 0.82,
            information_value: 0.65,
            viral_potential: 0.74,
            attention_retention: 0.55
        },
        insights: ["High emotional resonance makes this content prime for top-of-funnel", "Low retention suggests hook needs work"]
    },
    conversion: {
        friction: {
            cart_abandonment: 0.45,
            checkout_dropoff: 0.15,
            form_friction: 0.12
        },
        revenue_impact_monthly: 12500,
        insights: ["Cart abandonment is exceptionally high", "Streamlining checkout will yield +15% revenue"]
    },
    intent: {
        segment: "Solution Aware",
        confidence: 0.88,
        indicators: {
            high_intent_page_views: 4,
            pricing_page_time_sec: 120,
            return_visits: 3
        }
    }
};

const ProgressBar = ({ label, value, color }: { label: string, value: number, color: string }) => (
    <div className="bar-container">
        <div className="bar-header">
            <span>{label}</span>
            <span>{Math.round(value * 100)}%</span>
        </div>
        <div className="bar-track">
            <div
                className="bar-fill"
                style={{ width: `${value * 100}%`, backgroundColor: color }}
            ></div>
        </div>
    </div>
);

const DashboardInsights = () => {
    const [data, setData] = useState<typeof MOCK_DATA | null>(null);

    useEffect(() => {
        // Simulate fetching from Behavior Analyzer
        const timer = setTimeout(() => {
            setData(MOCK_DATA);
        }, 700);
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
                    <h1 className="page-title">Dashboard & Insights</h1>
                    <p className="page-subtitle">Behavior Signals and Cohort Tracking</p>
                </div>
                <span className="badge">LIVE DATA</span>
            </div>

            <div className="grid">
                {/* Engagement Card */}
                <div className="card glass-card">
                    <h2 className="card-title">Engagement Analysis</h2>
                    <ProgressBar label="Emotional Resonance" value={data.engagement.features.emotional_resonance} color="var(--primary)" />
                    <ProgressBar label="Viral Potential" value={data.engagement.features.viral_potential} color="var(--success)" />
                    <ProgressBar label="Information Value" value={data.engagement.features.information_value} color="var(--accent-purple)" />
                    <ProgressBar label="Attention Retention" value={data.engagement.features.attention_retention} color="var(--warning)" />

                    <div className="insights-box">
                        <h3 className="section-subtitle">Key Insights</h3>
                        <ul className="insight-list">
                            {data.engagement.insights.map((insight, idx) => (
                                <li key={idx}><div>{insight}</div></li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Conversion Card */}
                <div className="card glass-card">
                    <h2 className="card-title">Conversion Friction</h2>
                    <div className="stat-grid mb-6">
                        <div className="stat-item full-width stat-danger">
                            <div className="stat-label">Monthly Revenue Loss</div>
                            <div className="stat-text text-danger">
                                ${data.conversion.revenue_impact_monthly.toLocaleString()}
                            </div>
                        </div>
                    </div>

                    <ProgressBar label="Cart Abandonment" value={data.conversion.friction.cart_abandonment} color="var(--danger)" />
                    <ProgressBar label="Checkout Drop-off" value={data.conversion.friction.checkout_dropoff} color="var(--warning)" />
                    <ProgressBar label="Form Friction" value={data.conversion.friction.form_friction} color="var(--primary)" />

                    <div className="insights-box">
                        <h3 className="section-subtitle">Action Items</h3>
                        <ul className="insight-list">
                            {data.conversion.insights.map((insight, idx) => (
                                <li key={idx} className={idx === 0 ? 'critical' : 'positive'}><div>{insight}</div></li>
                            ))}
                        </ul>
                    </div>
                </div>

                {/* Intent Card */}
                <div className="card glass-card">
                    <h2 className="card-title">Intent Classification</h2>

                    <div className="intent-score-display">
                        <div className="icon-emoji">🔍</div>
                        <div className="metric-value-large text-primary">{data.intent.segment}</div>
                        <div className="text-muted">
                            Confidence Score: {Math.round(data.intent.confidence * 100)}%
                        </div>
                    </div>

                    <div className="stat-grid">
                        <div className="stat-item glass-blur">
                            <div className="stat-label">High Intent Views</div>
                            <div className="stat-text">{data.intent.indicators.high_intent_page_views}</div>
                        </div>
                        <div className="stat-item glass-blur">
                            <div className="stat-label">Return Visits</div>
                            <div className="stat-text">{data.intent.indicators.return_visits}</div>
                        </div>
                    </div>

                    <div className="recommendation-box">
                        <strong>Recommendation:</strong> Push retargeting ads focusing on product benefits and social proof.
                    </div>
                </div>
            </div>
        </div>
    );
};

export default DashboardInsights;
