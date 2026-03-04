'use client';
import { useEffect, useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import { intelligenceAPI, automationAPI, healthAPI } from '@/lib/api';
import {
    Zap, Shield, FlaskConical, Activity, TrendingUp, CheckCircle2,
    Clock, RefreshCw, AlertTriangle, Brain, ChevronRight, Loader2
} from 'lucide-react';

type Approval = { id: string; action: string };

function StatCard({ label, value, icon: Icon, color, sub }: any) {
    const colors: Record<string, string> = {
        indigo: 'rgba(99,102,241,0.15)',
        emerald: 'rgba(16,185,129,0.15)',
        amber: 'rgba(245,158,11,0.15)',
        rose: 'rgba(244,63,94,0.15)',
        cyan: 'rgba(6,182,212,0.15)',
        violet: 'rgba(139,92,246,0.15)',
    };
    const textColors: Record<string, string> = {
        indigo: '#818cf8', emerald: '#34d399', amber: '#fbbf24', rose: '#fb7185', cyan: '#22d3ee', violet: '#c084fc'
    };
    return (
        <div className="glass glass-hover animate-slide-up" style={{ padding: '1.25rem', display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <p style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.08em', textTransform: 'uppercase' }}>{label}</p>
                <div style={{ width: 32, height: 32, borderRadius: 8, background: colors[color] || colors.indigo, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Icon size={16} color={textColors[color] || textColors.indigo} />
                </div>
            </div>
            <p style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>{value}</p>
            {sub && <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{sub}</p>}
        </div>
    );
}

export default function Dashboard() {
    const [health, setHealth] = useState<any>(null);
    const [intel, setIntel] = useState<any>(null);
    const [approvals, setApprovals] = useState<Approval[]>([]);
    const [loading, setLoading] = useState(true);
    const [triggering, setTriggering] = useState(false);
    const [lastRefresh, setLastRefresh] = useState(new Date());

    const loadData = async () => {
        setLoading(true);
        try {
            const [h, i, a] = await Promise.allSettled([
                healthAPI.check(),
                intelligenceAPI.getDashboard(),
                automationAPI.getPending(),
            ]);
            if (h.status === 'fulfilled') setHealth(h.value.data);
            if (i.status === 'fulfilled') setIntel(i.value.data);
            if (a.status === 'fulfilled') setApprovals(a.value.data || []);
        } finally {
            setLoading(false);
            setLastRefresh(new Date());
        }
    };

    useEffect(() => { loadData(); }, []);

    const triggerDaily = async () => {
        setTriggering(true);
        try { await intelligenceAPI.triggerDaily(); } finally { setTriggering(false); loadData(); }
    };

    const approveAction = async (id: string) => {
        await automationAPI.approve(id);
        setApprovals(prev => prev.filter(a => a.id !== id));
    };
    const rejectAction = async (id: string) => {
        await automationAPI.reject(id);
        setApprovals(prev => prev.filter(a => a.id !== id));
    };

    return (
        <div style={{ display: 'flex' }}>
            <Sidebar />
            <main style={{ marginLeft: 220, flex: 1, minHeight: '100vh', padding: '2rem', background: 'var(--bg-base)' }}>

                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
                    <div>
                        <h1 style={{ fontWeight: 800, fontSize: '1.5rem', color: 'var(--text-primary)' }}>
                            <span className="gradient-text">Intelligence Dashboard</span>
                        </h1>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 4 }}>
                            Updated {lastRefresh.toLocaleTimeString()}
                        </p>
                    </div>
                    <div style={{ display: 'flex', gap: '0.75rem' }}>
                        <button className="btn-ghost" onClick={loadData} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
                        </button>
                        <button className="btn-primary" onClick={triggerDaily} disabled={triggering} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                            {triggering ? <Loader2 size={14} className="animate-spin" /> : <Zap size={14} />}
                            {triggering ? 'Triggering…' : 'Trigger Daily AI'}
                        </button>
                    </div>
                </div>

                {/* Stat Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(180px,1fr))', gap: '1rem', marginBottom: '2rem' }}>
                    <StatCard label="System Status" icon={CheckCircle2} color="emerald" value={health ? '● Online' : '○ Checking'} sub={health?.service || '—'} />
                    <StatCard label="Pending Actions" icon={AlertTriangle} color="amber" value={approvals.length} sub="require review" />
                    <StatCard label="Autonomy Mode" icon={Brain} color="indigo" value="Active" sub="intelligence core" />
                    <StatCard label="AI Experiments" icon={FlaskConical} color="cyan" value="Live" sub="sandbox running" />
                    <StatCard label="Daily Execution" icon={Zap} color="violet" value="Scheduled" sub="next cycle: auto" />
                    <StatCard label="Risk State" icon={Shield} color="emerald" value="CLEAN" sub="no escalations" />
                </div>

                {/* Main Grid */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>

                    {/* Intelligence Feed */}
                    <div className="glass" style={{ padding: '1.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '1.25rem' }}>
                            <Activity size={16} color="var(--indigo)" />
                            <h2 style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-primary)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>Intelligence Stream</h2>
                        </div>

                        {loading ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                {[1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: 52 }} />)}
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {[
                                    { type: 'AI_EXECUTION', msg: 'Budget scaled +12% on Q3_Meta campaign', time: '2m ago', color: 'emerald' },
                                    { type: 'DRIFT_ALERT', msg: 'Confidence decay detected on RTG_Global', time: '14m ago', color: 'amber' },
                                    { type: 'EXPERIMENT', msg: 'New creative variant launched in sandbox', time: '1h ago', color: 'cyan' },
                                    { type: 'CALIBRATION', msg: 'Genesis approved threshold adjustment', time: '3h ago', color: 'violet' },
                                ].map((ev, i) => {
                                    const colors: any = { emerald: '#34d399', amber: '#fbbf24', cyan: '#22d3ee', violet: '#c084fc' };
                                    return (
                                        <div key={i} style={{ display: 'flex', gap: '0.75rem', alignItems: 'flex-start', padding: '0.75rem', borderRadius: 10, background: 'rgba(255,255,255,0.02)' }}>
                                            <div style={{ width: 7, height: 7, borderRadius: '50%', background: colors[ev.color], marginTop: 5, flexShrink: 0, boxShadow: `0 0 6px ${colors[ev.color]}` }} />
                                            <div style={{ flex: 1 }}>
                                                <p style={{ fontSize: '0.78rem', color: 'var(--text-primary)', fontWeight: 500 }}>{ev.msg}</p>
                                                <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: 2 }}>{ev.type} · {ev.time}</p>
                                            </div>
                                        </div>
                                    );
                                })}
                                {intel && (
                                    <div style={{ padding: '0.75rem', borderRadius: 10, background: 'rgba(99,102,241,0.08)', border: '1px solid rgba(99,102,241,0.15)' }}>
                                        <p style={{ fontSize: '0.75rem', color: '#a5b4fc', fontWeight: 600 }}>Backend says:</p>
                                        <p style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: 4 }}>{JSON.stringify(intel)}</p>
                                    </div>
                                )}
                            </div>
                        )}
                    </div>

                    {/* Pending Approvals */}
                    <div className="glass" style={{ padding: '1.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.25rem' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                <Shield size={16} color="var(--amber)" />
                                <h2 style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-primary)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>Pending Approvals</h2>
                            </div>
                            {approvals.length > 0 && <span className="badge badge-warning">{approvals.length} pending</span>}
                        </div>

                        {loading ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                {[1, 2].map(i => <div key={i} className="skeleton" style={{ height: 70 }} />)}
                            </div>
                        ) : approvals.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '2rem 1rem' }}>
                                <CheckCircle2 size={32} color="var(--emerald)" style={{ margin: '0 auto 0.75rem' }} />
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 500 }}>No pending actions</p>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: 4 }}>AI is executing within envelope limits</p>
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {approvals.map((a) => (
                                    <div key={a.id} style={{ padding: '0.9rem 1rem', borderRadius: 10, background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.12)' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
                                            <div>
                                                <p style={{ fontSize: '0.75rem', fontFamily: 'monospace', color: 'var(--text-muted)' }}>{a.id}</p>
                                                <p style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginTop: 2 }}>{a.action}</p>
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <button className="btn-primary" onClick={() => approveAction(a.id)} style={{ fontSize: '0.75rem', padding: '0.35rem 0.9rem' }}>Approve</button>
                                            <button className="btn-ghost" onClick={() => rejectAction(a.id)} style={{ fontSize: '0.75rem', padding: '0.35rem 0.9rem', color: 'var(--rose)' }}>Reject</button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* System Health */}
                    <div className="glass" style={{ padding: '1.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '1.25rem' }}>
                            <TrendingUp size={16} color="var(--emerald)" />
                            <h2 style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-primary)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>Intelligence Layers</h2>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                            {[
                                { name: 'Atlas (Data Layer)', status: 'online' },
                                { name: 'Genesis (Governance)', status: 'online' },
                                { name: 'Captain (Diagnose+Execute)', status: 'online' },
                                { name: 'Hawkeye (Creative AI)', status: 'online' },
                                { name: 'Pulse (Macro Awareness)', status: 'online' },
                                { name: 'Sentinel (Monitoring)', status: 'online' },
                                { name: 'Forge (Experimentation)', status: 'online' },
                                { name: 'Calibration (Tuning)', status: 'online' },
                            ].map(s => (
                                <div key={s.name} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0.5rem 0.75rem', borderRadius: 8, background: 'rgba(255,255,255,0.02)' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <div style={{ width: 6, height: 6, borderRadius: '50%' }} className={`dot-${s.status} animate-pulse-glow`} />
                                        <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{s.name}</span>
                                    </div>
                                    <span style={{ fontSize: '0.68rem', fontWeight: 700, color: '#34d399' }}>ONLINE</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="glass" style={{ padding: '1.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '1.25rem' }}>
                            <Clock size={16} color="var(--violet)" />
                            <h2 style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-primary)', letterSpacing: '0.05em', textTransform: 'uppercase' }}>Quick Actions</h2>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                            {[
                                { label: 'View Companies', href: '/companies', color: 'indigo' },
                                { label: 'Review Automation', href: '/automation', color: 'amber' },
                                { label: 'Run Competitor AI', href: '/competitor', color: 'cyan' },
                            ].map(a => (
                                <a key={a.href} href={a.href} style={{
                                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                    padding: '0.85rem 1rem', borderRadius: 10,
                                    background: 'rgba(255,255,255,0.02)',
                                    border: '1px solid var(--border)',
                                    color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: 500,
                                    textDecoration: 'none', transition: 'all 0.18s ease',
                                }}
                                    onMouseEnter={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.05)'; (e.currentTarget as HTMLElement).style.color = 'var(--text-primary)'; }}
                                    onMouseLeave={e => { (e.currentTarget as HTMLElement).style.background = 'rgba(255,255,255,0.02)'; (e.currentTarget as HTMLElement).style.color = 'var(--text-secondary)'; }}
                                >
                                    {a.label}
                                    <ChevronRight size={14} />
                                </a>
                            ))}
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
}
