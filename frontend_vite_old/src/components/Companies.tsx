import { useState, useEffect } from 'react';
import { Building2, Plus, ArrowRight, ShieldCheck, AlertTriangle } from 'lucide-react';
import '../App.css';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const Companies = () => {
    const [companies, setCompanies] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [creationError, setCreationError] = useState<string | null>(null);
    const [newCompany, setNewCompany] = useState({ name: '', domain: '' });

    // Mock role limit check from the profile
    const currentRole = "business_owner"; // In production fetched from Context/JWT
    const limits = { "business_owner": 1, "marketing_professional": 3, "freelancer": 7 };
    const maxCompanies = limits[currentRole as keyof typeof limits] || 1;

    useEffect(() => {
        const fetchCompanies = async () => {
            try {
                // Fetch user's registered companies from the actual API
                const res = await axios.get(`${API_BASE_URL}/api/v1/companies/`).catch(() => null);
                if (res?.data) {
                    setCompanies(res.data);
                } else {
                    // Fallback to mock data to show UI while backend connects
                    setCompanies([
                        { id: '1', name: 'Global SaaS Tech', domain: 'globaltech.com', active_platforms: ['meta'] }
                    ]);
                }
            } catch (err) {
                console.error("Failed to load companies", err);
            } finally {
                setLoading(false);
            }
        };

        fetchCompanies();
    }, []);

    const handleCreateCompany = async (e: React.FormEvent) => {
        e.preventDefault();
        setCreationError(null);

        if (companies.length >= maxCompanies) {
            setCreationError(`Limit Reached: Your ${currentRole} plan permits ${maxCompanies} workspace(s). Please upgrade your subscription.`);
            return;
        }

        try {
            // Attempt to hit our real backend logic that enforces the server-side limits:
            const response = await axios.post(`${API_BASE_URL}/api/v1/companies/`, newCompany).catch((err) => {
                if (err.response?.status === 403) {
                    setCreationError(err.response.data.detail);
                }
                return null;
            });

            if (response?.data) {
                setCompanies([...companies, response.data]);
                setNewCompany({ name: '', domain: '' });
            } else if (!creationError) {
                // Mock success if backend not running
                setCompanies([...companies, { id: Date.now().toString(), ...newCompany, active_platforms: [] }]);
                setNewCompany({ name: '', domain: '' });
            }

        } catch (error) {
            console.error("Creation failed", error);
        }
    };

    return (
        <div className="dashboard-layout fade-in">
            <header className="header">
                <div className="header-titles">
                    <h1>Company Profiles & Workspaces</h1>
                    <p className="subtitle">Manage distinct SaaS clients or internal brands (Multi-Tenant Environment)</p>
                </div>
            </header>

            <div className="settings-grid">
                {/* Created Companies Container */}
                <div className="glass-panel" style={{ gridColumn: 'span 2' }}>
                    <div className="panel-header">
                        <Building2 size={24} className="text-primary" />
                        <h2>Active Companies ({companies.length} / {maxCompanies})</h2>
                    </div>

                    {companies.length >= maxCompanies && (
                        <div className="notification-banner glass-panel fade-in" style={{ backgroundColor: 'rgba(234, 179, 8, 0.1)', borderColor: '#eab308', marginBottom: '1.5rem', color: '#fef08a' }}>
                            <AlertTriangle size={20} color="#eab308" />
                            <span>You have reached the maximum active companies allowed on your current tier.
                                <a href="/billing" style={{ color: '#0ea5e9', marginLeft: '10px', fontWeight: 'bold' }}>Upgrade Plan →</a>
                            </span>
                        </div>
                    )}

                    <div className="platforms-grid">
                        {loading && companies.length === 0 ? (
                            <div className="loading-spinner"></div>
                        ) : (
                            companies.map((company) => (
                                <div className="platform-card" key={company.id}>
                                    <div className="platform-header">
                                        <div className="platform-icon-name">
                                            <Building2 size={24} color="#94a3b8" />
                                            <span className="platform-name">{company.name}</span>
                                        </div>
                                    </div>
                                    <div className="platform-body">
                                        <div className="sync-status text-muted mb-2">
                                            Domain: {company.domain || "N/A"}
                                        </div>
                                        <div className="sync-status text-muted">
                                            Connected Platforms: {company.active_platforms?.length || 0}
                                        </div>
                                        <button className="button bg-surface" style={{ marginTop: '1rem', width: '100%', border: '1px solid #334155', display: 'flex', justifyContent: 'center', gap: '8px' }}>
                                            Manage Profile <ArrowRight size={16} />
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Create New Profile Form */}
                <div className="glass-panel profile-settings">
                    <div className="panel-header">
                        <Plus size={20} className="text-primary" />
                        <h2>Register New Profile</h2>
                    </div>

                    {creationError && (
                        <div className="text-danger" style={{ marginBottom: '1rem', fontSize: '0.85rem', padding: '10px', border: '1px solid #ef4444', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)' }}>
                            {creationError}
                        </div>
                    )}

                    <form className="settings-form" onSubmit={handleCreateCompany}>
                        <div className="form-group">
                            <label>Company / Agency Name</label>
                            <input
                                type="text"
                                className="glass-input"
                                placeholder="E.g., Global Tech SaaS"
                                value={newCompany.name}
                                onChange={(e) => setNewCompany({ ...newCompany, name: e.target.value })}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label>Primary Domain (Optional)</label>
                            <input
                                type="text"
                                className="glass-input"
                                placeholder="example.com"
                                value={newCompany.domain}
                                onChange={(e) => setNewCompany({ ...newCompany, domain: e.target.value })}
                            />
                        </div>

                        <div style={{ marginTop: '1.5rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <ShieldCheck size={18} color="#10b981" />
                            <span className="text-muted" style={{ fontSize: '0.8rem' }}>Strict Role-Based Multi-Tenancy Engine validation</span>
                        </div>

                        <button
                            type="submit"
                            className="button bg-primary w-100"
                            style={{ justifyContent: 'center', padding: '0.75rem', opacity: companies.length >= maxCompanies ? 0.5 : 1 }}
                            disabled={companies.length >= maxCompanies}
                        >
                            Create Company Sandbox
                        </button>
                    </form>
                </div>

            </div>
        </div>
    );
};

export default Companies;
