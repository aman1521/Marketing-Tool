import { useState } from 'react';
import { CreditCard, CheckCircle2, Star, Shield, ArrowRight } from 'lucide-react';
import '../App.css';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const Billing = () => {
    const [loadingPlan, setLoadingPlan] = useState<string | null>(null);

    const plans = [
        {
            id: 'price_business_owner_123',
            name: 'Business Owner',
            price: 49,
            limits: '1 Company Profile',
            features: ['Daily Intelligence Engine', 'Basic Multi-Tenant Setup', 'Manual Automations'],
            recommended: false
        },
        {
            id: 'price_marketing_pro_456',
            name: 'Marketing Professional',
            price: 99,
            limits: '3 Company Profiles',
            features: ['Advanced Qdrant Competitor Insights', 'Real-time Safety Layer', 'Automated Execution Pipeline'],
            recommended: true
        },
        {
            id: 'price_freelancer_789',
            name: 'Freelancer / Agency',
            price: 199,
            limits: '7 Company Profiles',
            features: ['Infinite Cross-tenant Insights', 'White-labeled Dashboards', 'Dedicated Backend Queues (Celery)'],
            recommended: false
        }
    ];

    const handleCheckout = async (priceId: string) => {
        setLoadingPlan(priceId);
        try {
            // Trigger FastAPI Backend (Stripe Service)
            const response = await axios.post(`${API_BASE_URL}/api/v1/subscriptions/checkout`, null, {
                params: {
                    price_id: priceId,
                    success_url: "http://localhost:5173/companies?success=true",
                    cancel_url: "http://localhost:5173/billing?canceled=true"
                }
            }).catch(() => null);

            if (response?.data?.url) {
                window.location.href = response.data.url;
            } else {
                // Mock redirect if backend isn't linked
                setTimeout(() => {
                    alert("Stripe Backend is not connected. This would redirect to Stripe Checkout using: " + priceId);
                    setLoadingPlan(null);
                }, 800);
            }
        } catch (error) {
            console.error(error);
            setLoadingPlan(null);
        }
    };

    return (
        <div className="dashboard-layout fade-in">
            <header className="header">
                <div className="header-titles">
                    <h1>Billing & Subscription Scaling</h1>
                    <p className="subtitle">Securely manage your SaaS tenant allocation and upgrade limits.</p>
                </div>
            </header>

            <div className="billing-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '2rem', marginTop: '2rem' }}>
                {plans.map((plan) => (
                    <div className={`glass-panel pricing-card ${plan.recommended ? 'recommended' : ''}`} key={plan.id} style={{
                        display: 'flex', flexDirection: 'column',
                        border: plan.recommended ? '1px solid #0ea5e9' : '1px solid rgba(255,255,255,0.05)',
                        position: 'relative', overflow: 'hidden'
                    }}>
                        {plan.recommended && (
                            <div style={{ position: 'absolute', top: 0, right: 0, background: '#0ea5e9', color: '#fff', padding: '4px 12px', fontSize: '0.75rem', fontWeight: 'bold', borderBottomLeftRadius: '8px' }}>
                                MOST POPULAR
                            </div>
                        )}
                        <div className="panel-header" style={{ marginBottom: '0.5rem' }}>
                            {plan.recommended ? <Star size={24} color="#0ea5e9" /> : <Shield size={24} className="text-muted" />}
                            <h2 style={{ fontSize: '1.25rem' }}>{plan.name}</h2>
                        </div>

                        <div className="price" style={{ fontSize: '2.5rem', fontWeight: 700, margin: '1rem 0' }}>
                            ${plan.price}<span style={{ fontSize: '1rem', color: '#94a3b8', fontWeight: 400 }}> / month</span>
                        </div>

                        <div className="limits text-primary" style={{ marginBottom: '1.5rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <Building2 size={16} /> Max Allocation: {plan.limits}
                        </div>

                        <ul style={{ listStyle: 'none', padding: 0, marginBottom: '2rem', flexGrow: 1 }}>
                            {plan.features.map((feature, i) => (
                                <li key={i} style={{ display: 'flex', alignItems: 'start', gap: '10px', marginBottom: '0.75rem', fontSize: '0.95rem' }}>
                                    <CheckCircle2 size={18} color="#10b981" style={{ flexShrink: 0, marginTop: '2px' }} />
                                    <span>{feature}</span>
                                </li>
                            ))}
                        </ul>

                        <button
                            className={`button ${plan.recommended ? 'bg-primary' : 'bg-surface'}`}
                            style={{ marginTop: 'auto', justifyContent: 'center', padding: '1rem', width: '100%', border: plan.recommended ? 'none' : '1px solid #334155' }}
                            onClick={() => handleCheckout(plan.id)}
                            disabled={loadingPlan === plan.id}
                        >
                            {loadingPlan === plan.id ? 'Connecting to Stripe...' : 'Upgrade Tenant Tier'} <CreditCard size={18} style={{ marginLeft: '8px' }} />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
};

// Simple Mock component local import since Building2 isn't imported from lucide above
import { Building2 } from 'lucide-react';

export default Billing;
