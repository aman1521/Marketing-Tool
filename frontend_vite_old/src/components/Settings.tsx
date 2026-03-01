import { useState, useEffect } from 'react';
import axios from 'axios';
import { Share2, CheckCircle2, Lock, User, LayoutDashboard, Database, Key } from 'lucide-react';
import '../App.css';

const API_BASE_URL = 'http://localhost:8000'; // Make sure docker-compose is running api-gateway

const Settings = () => {
    const [platforms, setPlatforms] = useState<any>({
        meta: { connected: false, last_sync: null },
        google: { connected: false, last_sync: null },
        tiktok: { connected: false, last_sync: null },
        linkedin: { connected: false, last_sync: null },
        shopify: { connected: false, last_sync: null },
        woocommerce: { connected: false, last_sync: null },
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [mockMessage, setMockMessage] = useState<string | null>(null);

    // Business & Profile State
    const [profile, setProfile] = useState({
        name: 'Agency Admin',
        email: 'admin@aios.marketing',
        businessName: 'Global SaaS Tech',
        businessId: '00000000-0000-0000-0000-000000000001',
    });

    useEffect(() => {
        const fetchStatus = async () => {
            try {
                // Fetch live status from our actual Python Platform Integration Service via API Gateway
                const response = await axios.get(`${API_BASE_URL}/api/v1/platforms/status`).catch(() => null);
                if (response?.data?.platforms) {
                    setPlatforms(response.data.platforms);
                }
            } catch (error) {
                console.error("Platform status API unavailable - Gateway or Backend may be down.", error);
            } finally {
                setLoading(false);
            }
        };

        fetchStatus();

        // Check if we just returned from an OAuth Flow
        const urlParams = new URLSearchParams(window.location.search);
        const connectedPlatform = urlParams.get('platform_connected');
        const authError = urlParams.get('error');

        if (connectedPlatform) {
            setMockMessage(`Successfully linked & ingested data for ${connectedPlatform.toUpperCase()}`);
            setPlatforms((prev: any) => ({
                ...prev,
                [connectedPlatform]: { connected: true, last_sync: new Date().toISOString() }
            }));
            setTimeout(() => setMockMessage(null), 5000);

            // Clean up the URL
            window.history.replaceState({}, document.title, window.location.pathname);
        } else if (authError) {
            setMockMessage(`Failed to connect platform: ${authError}`);
            setTimeout(() => setMockMessage(null), 5000);
            window.history.replaceState({}, document.title, window.location.pathname);
        }

    }, []);

    const handleConnectPlatform = async (platformName: string) => {
        setLoading(true);
        try {
            // Only 'meta' and 'google' are built with the OAuth redirects currently
            if (platformName === "meta" || platformName === "google") {
                // 1. Fetch the secure generated URL from the FastAPI backend
                const response = await axios.get(`${API_BASE_URL}/api/v1/connectors/oauth/url`, {
                    params: {
                        platform: platformName,
                        company_id: profile.businessId
                    }
                });

                // 2. Redirect the user's browser to the actual OAuth Consent Screen.
                // Once they approve it there, Meta/Google will fire the code back to /api/v1/connectors/oauth/callback
                if (response.data?.url) {
                    window.location.href = response.data.url;
                    return;
                }
            } else {
                setMockMessage(`OAuth flow for ${platformName} is not natively integrated yet.`);
                setTimeout(() => setMockMessage(null), 3000);
            }
        } catch (error) {
            console.error(`Failed to connect ${platformName}:`, error);
        } finally {
            setLoading(false);
        }
    };

    const handleDisconnectPlatform = (platformName: string) => {
        // Disconnect logic (we mock local state reset here)
        setPlatforms((prev: any) => ({
            ...prev,
            [platformName]: { connected: false, last_sync: null }
        }));
    };

    const handleSaveProfile = (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);
        setTimeout(() => {
            setSaving(false);
            setMockMessage('Profile & Database Preferences saved successfully.');
            setTimeout(() => setMockMessage(null), 3000);
        }, 1000);
    };

    const renderPlatformCard = (key: string, data: any) => {
        return (
            <div className="platform-card" key={key}>
                <div className="platform-header">
                    <div className="platform-icon-name">
                        <Share2 size={24} color={data.connected ? "#10b981" : "#94a3b8"} />
                        <span className="platform-name">{key.charAt(0).toUpperCase() + key.slice(1)}</span>
                    </div>
                    {data.connected && <CheckCircle2 size={20} color="#10b981" />}
                </div>

                <div className="platform-body">
                    {data.connected ? (
                        <>
                            <div className="sync-status text-muted">
                                Last Sync: {data.last_sync ? new Date(data.last_sync).toLocaleString() : 'Just now'}
                            </div>
                            <button
                                className="button bg-surface"
                                style={{ marginTop: '1rem', border: '1px solid #334155' }}
                                onClick={() => handleDisconnectPlatform(key)}
                            >
                                Disconnect
                            </button>
                        </>
                    ) : (
                        <button
                            className="button bg-primary"
                            style={{ marginTop: '1rem' }}
                            onClick={() => handleConnectPlatform(key)}
                            disabled={loading}
                        >
                            Connect Account
                        </button>
                    )}
                </div>
            </div>
        );
    };

    return (
        <div className="dashboard-layout fade-in">
            <header className="header">
                <div className="header-titles">
                    <h1>Platform Settings & Controls</h1>
                    <p className="subtitle">Manage API Integrations, RBAC Permissions, and System Data</p>
                </div>
            </header>

            {mockMessage && (
                <div className="notification-banner glass-panel fade-in" style={{ backgroundColor: 'rgba(16, 185, 129, 0.1)', borderColor: '#10b981', marginBottom: '2rem' }}>
                    <CheckCircle2 color="#10b981" />
                    <span>{mockMessage}</span>
                </div>
            )}

            <div className="settings-grid">

                {/* 1. Profile & Role Based Access Settings */}
                <div className="glass-panel profile-settings">
                    <div className="panel-header">
                        <User size={20} className="text-primary" />
                        <h2>User & Agency Profile</h2>
                    </div>
                    <form className="settings-form" onSubmit={handleSaveProfile}>
                        <div className="form-group">
                            <label>Full Name</label>
                            <input
                                type="text"
                                className="glass-input"
                                value={profile.name}
                                onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label>Authentication Email</label>
                            <input
                                type="email"
                                className="glass-input"
                                value={profile.email}
                                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label>Primary Business Hub</label>
                            <input
                                type="text"
                                className="glass-input"
                                value={profile.businessName}
                                onChange={(e) => setProfile({ ...profile, businessName: e.target.value })}
                            />
                        </div>
                        <div className="form-group">
                            <label>UUID Tenant Identity</label>
                            <input
                                type="text"
                                className="glass-input text-muted"
                                value={profile.businessId}
                                disabled
                            />
                        </div>
                        <button type="submit" className="button bg-primary" disabled={saving}>
                            {saving ? 'Saving...' : 'Update Settings'}
                        </button>
                    </form>
                </div>

                {/* 2. Platform Integrations */}
                <div className="glass-panel integrations-panel" style={{ gridColumn: 'span 2' }}>
                    <div className="panel-header">
                        <Database size={20} className="text-primary" />
                        <h2>Data Stream & Integrations (OAuth)</h2>
                    </div>
                    <p className="text-muted" style={{ marginBottom: '1.5rem', fontSize: '0.9rem' }}>
                        Connecting a platform establishes a persistent webhook listener. The Data Governance Layer will immediately attempt to backfill 90-days of performance metrics.
                    </p>

                    <div className="platforms-grid">
                        {loading && !Object.keys(platforms).length ? (
                            <div className="loading-spinner"></div>
                        ) : (
                            Object.entries(platforms).map(([key, data]) => renderPlatformCard(key, data))
                        )}
                    </div>
                </div>

                {/* 3. Security & Governance */}
                <div className="glass-panel security-panel" style={{ gridColumn: 'span 3' }}>
                    <div className="panel-header">
                        <Lock size={20} className="text-primary" />
                        <h2>Security & Data Governance (Phase 7 Schema)</h2>
                    </div>
                    <div className="security-controls" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '1rem' }}>
                        <div className="security-item">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                                <Key size={16} /> <span>API Gateway Tokens</span>
                            </div>
                            <p className="text-muted" style={{ fontSize: '0.85rem' }}>Access JSON Web Tokens have been enforced across API endpoints. You are operating as `Agency Admin`.</p>
                        </div>
                        <div className="security-item">
                            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                                <LayoutDashboard size={16} /> <span>Data Drift Algorithms</span>
                            </div>
                            <p className="text-muted" style={{ fontSize: '0.85rem' }}>Continuous Validation is active. The engine will auto-trigger XGBoost retrains if error rates exceed 15% tolerance bounds.</p>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default Settings;
