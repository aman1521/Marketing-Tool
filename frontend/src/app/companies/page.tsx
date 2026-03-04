'use client';
import { useEffect, useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import { companiesAPI, connectorsAPI } from '@/lib/api';
import { Building2, Plus, Loader2, Link2, ChevronRight, RefreshCw, X } from 'lucide-react';

type Company = { id: string; name: string; industry: string; target_audience?: string };
type Platform = { platform: string; status: string; last_sync: string | null };

const PLATFORM_META: Record<string, { logo: string; color: string }> = {
    meta: { logo: '𝕄', color: '#1877f2' },
    google: { logo: 'G', color: '#4285f4' },
    tiktok: { logo: '⧫', color: '#fe2c55' },
    linkedin: { logo: 'in', color: '#0a66c2' },
    twitter: { logo: '𝕏', color: '#000000' },
    reddit: { logo: '⬤', color: '#ff4500' },
};

export default function CompaniesPage() {
    const [companies, setCompanies] = useState<Company[]>([]);
    const [loading, setLoading] = useState(true);
    const [showModal, setShowModal] = useState(false);
    const [creating, setCreating] = useState(false);
    const [form, setForm] = useState({ name: '', industry: '', target_audience: '' });
    const [error, setError] = useState('');
    const [selected, setSelected] = useState<Company | null>(null);
    const [platforms, setPlatforms] = useState<Platform[]>([]);
    const [loadingPlat, setLoadingPlat] = useState(false);

    const load = async () => {
        setLoading(true);
        try {
            const res = await companiesAPI.list();
            setCompanies(res.data || []);
        } catch { setCompanies([]); }
        finally { setLoading(false); }
    };

    useEffect(() => { load(); }, []);

    const selectCompany = async (c: Company) => {
        setSelected(c);
        setLoadingPlat(true);
        try {
            const res = await connectorsAPI.getPlatforms(c.id);
            setPlatforms(res.data || []);
        } catch { setPlatforms([]); }
        finally { setLoadingPlat(false); }
    };

    const createCompany = async (e: React.FormEvent) => {
        e.preventDefault(); setCreating(true); setError('');
        try {
            await companiesAPI.create(form);
            setShowModal(false);
            setForm({ name: '', industry: '', target_audience: '' });
            load();
        } catch (err: any) {
            setError(err?.response?.data?.detail || 'Failed to create company');
        } finally { setCreating(false); }
    };

    const connectPlatform = async (platform: string) => {
        if (!selected) return;
        try {
            const res = await connectorsAPI.connectPlatform(platform, selected.id);
            const url = res.data?.authorization_url;
            if (url) window.location.href = url;
        } catch (err: any) {
            alert(err?.response?.data?.detail || 'Connection failed');
        }
    };

    return (
        <div style={{ display: 'flex' }}>
            <Sidebar />
            <main style={{ marginLeft: 220, flex: 1, minHeight: '100vh', padding: '2rem', background: 'var(--bg-base)' }}>

                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
                    <div>
                        <h1 style={{ fontWeight: 800, fontSize: '1.5rem' }}><span className="gradient-text">Companies</span></h1>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 4 }}>Manage tenants and platform connections</p>
                    </div>
                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                        <button className="btn-ghost" onClick={load} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
                        </button>
                        <button className="btn-primary" onClick={() => setShowModal(true)} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <Plus size={14} /> New Company
                        </button>
                    </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 1.5fr' : '1fr', gap: '1.5rem' }}>
                    {/* Company List */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                        {loading ? (
                            [1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: 80 }} />)
                        ) : companies.length === 0 ? (
                            <div className="glass" style={{ padding: '3rem', textAlign: 'center' }}>
                                <Building2 size={40} color="var(--text-muted)" style={{ margin: '0 auto 1rem' }} />
                                <p style={{ color: 'var(--text-secondary)', fontWeight: 600 }}>No companies yet</p>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 6 }}>Create your first company to get started</p>
                                <button className="btn-primary" onClick={() => setShowModal(true)} style={{ marginTop: '1.25rem', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                                    <Plus size={14} /> Create Company
                                </button>
                            </div>
                        ) : companies.map(c => (
                            <div key={c.id} onClick={() => selectCompany(c)} className="glass glass-hover"
                                style={{ padding: '1.1rem 1.25rem', cursor: 'pointer', borderColor: selected?.id === c.id ? 'rgba(99,102,241,0.4)' : undefined, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.9rem' }}>
                                    <div style={{ width: 40, height: 40, borderRadius: 10, background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem', fontWeight: 800, color: 'white' }}>
                                        {c.name.charAt(0)}
                                    </div>
                                    <div>
                                        <p style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.9rem' }}>{c.name}</p>
                                        <p style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 2 }}>{c.industry}</p>
                                    </div>
                                </div>
                                <ChevronRight size={16} color="var(--text-muted)" />
                            </div>
                        ))}
                    </div>

                    {/* Platform Panel */}
                    {selected && (
                        <div className="glass animate-slide-up" style={{ padding: '1.5rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                    <Link2 size={16} color="var(--indigo)" />
                                    <h2 style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-primary)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>
                                        {selected.name} · Platforms
                                    </h2>
                                </div>
                                <button onClick={() => setSelected(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}><X size={16} /></button>
                            </div>

                            {loadingPlat ? (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                    {[1, 2, 3, 4, 5, 6].map(i => <div key={i} className="skeleton" style={{ height: 58 }} />)}
                                </div>
                            ) : (
                                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                                    {(['meta', 'google', 'tiktok', 'linkedin', 'twitter', 'reddit']).map(p => {
                                        const plat = platforms.find(pl => pl.platform === p);
                                        const connected = plat?.status === 'connected';
                                        const meta = PLATFORM_META[p];
                                        return (
                                            <div key={p} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.85rem 1rem', borderRadius: 10, background: 'rgba(255,255,255,0.025)', border: '1px solid var(--border)' }}>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                                                    <div style={{ width: 34, height: 34, borderRadius: 8, background: connected ? `${meta.color}22` : 'rgba(255,255,255,0.04)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.9rem', fontWeight: 800, color: connected ? meta.color : 'var(--text-muted)' }}>
                                                        {meta.logo}
                                                    </div>
                                                    <div>
                                                        <p style={{ fontWeight: 600, fontSize: '0.82rem', color: 'var(--text-primary)', textTransform: 'capitalize' }}>{p}</p>
                                                        <p style={{ fontSize: '0.68rem', color: connected ? '#34d399' : 'var(--text-muted)' }}>
                                                            {connected ? `Connected · synced ${plat?.last_sync ? new Date(plat.last_sync).toLocaleDateString() : 'recently'}` : 'Not connected'}
                                                        </p>
                                                    </div>
                                                </div>
                                                {connected ? (
                                                    <a href={`/companies/${selected.id}?platform=${p}`} className="btn-ghost" style={{ fontSize: '0.72rem', padding: '0.3rem 0.75rem', textDecoration: 'none' }}>View Data</a>
                                                ) : (
                                                    <button className="btn-primary" onClick={() => connectPlatform(p)} style={{ fontSize: '0.72rem', padding: '0.3rem 0.75rem' }}>Connect</button>
                                                )}
                                            </div>
                                        );
                                    })}
                                </div>
                            )}
                        </div>
                    )}
                </div>

                {/* Create Company Modal */}
                {showModal && (
                    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, backdropFilter: 'blur(4px)' }}>
                        <div className="glass animate-slide-up" style={{ width: '100%', maxWidth: 440, padding: '2rem', margin: '1rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem' }}>
                                <h2 style={{ fontWeight: 700, fontSize: '1.1rem' }}>Create Company</h2>
                                <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)' }}><X size={18} /></button>
                            </div>
                            <form onSubmit={createCompany} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                                {(['name', 'industry', 'target_audience'] as const).map(field => (
                                    <div key={field}>
                                        <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', display: 'block', marginBottom: 6, textTransform: 'uppercase' }}>{field.replace('_', ' ')}</label>
                                        <input className="input-dark" value={form[field]} onChange={e => setForm(f => ({ ...f, [field]: e.target.value }))} placeholder={field === 'name' ? 'Acme Corp' : field === 'industry' ? 'eCommerce' : 'D2C Shoppers 25-35'} required />
                                    </div>
                                ))}
                                {error && <div style={{ background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.2)', borderRadius: 8, padding: '0.65rem', fontSize: '0.8rem', color: '#fb7185' }}>{error}</div>}
                                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem' }}>
                                    <button type="button" className="btn-ghost" onClick={() => setShowModal(false)} style={{ flex: 1 }}>Cancel</button>
                                    <button type="submit" className="btn-primary" disabled={creating} style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 6 }}>
                                        {creating ? <><Loader2 size={14} className="animate-spin" /> Creating…</> : 'Create'}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
}
