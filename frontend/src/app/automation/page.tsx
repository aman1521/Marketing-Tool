'use client';
import { useEffect, useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import { automationAPI } from '@/lib/api';
import { Shield, CheckCircle2, XCircle, RefreshCw, Loader2, AlertTriangle } from 'lucide-react';

type Approval = { id: string; action: string };

export default function AutomationPage() {
    const [approvals, setApprovals] = useState<Approval[]>([]);
    const [loading, setLoading] = useState(true);
    const [actioning, setActioning] = useState<string | null>(null);
    const [history, setHistory] = useState<{ id: string; action: string; decision: string; at: string }[]>([]);

    const load = async () => {
        setLoading(true);
        try { const res = await automationAPI.getPending(); setApprovals(res.data || []); }
        catch { setApprovals([]); } finally { setLoading(false); }
    };

    useEffect(() => { load(); }, []);

    const decide = async (id: string, decision: 'approve' | 'reject') => {
        setActioning(id);
        try {
            if (decision === 'approve') await automationAPI.approve(id);
            else await automationAPI.reject(id);
            const item = approvals.find(a => a.id === id);
            if (item) setHistory(h => [{ id, action: item.action, decision, at: new Date().toLocaleTimeString() }, ...h]);
            setApprovals(prev => prev.filter(a => a.id !== id));
        } finally { setActioning(null); }
    };

    return (
        <div style={{ display: 'flex' }}>
            <Sidebar />
            <main style={{ marginLeft: 220, flex: 1, minHeight: '100vh', padding: '2rem', background: 'var(--bg-base)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                    <div>
                        <h1 style={{ fontWeight: 800, fontSize: '1.5rem' }}><span className="gradient-text">Automation Control</span></h1>
                        <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 4 }}>Review and approve AI-proposed execution actions</p>
                    </div>
                    <button className="btn-ghost" onClick={load} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh
                    </button>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '1.5rem' }}>
                    {/* Pending Actions */}
                    <div className="glass" style={{ padding: '1.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '1.25rem' }}>
                            <AlertTriangle size={16} color="var(--amber)" />
                            <h2 style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Pending Actions</h2>
                            {approvals.length > 0 && <span className="badge badge-warning" style={{ marginLeft: 'auto' }}>{approvals.length}</span>}
                        </div>

                        {loading ? (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                {[1, 2, 3].map(i => <div key={i} className="skeleton" style={{ height: 80 }} />)}
                            </div>
                        ) : approvals.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
                                <CheckCircle2 size={40} color="var(--emerald)" style={{ margin: '0 auto 1rem' }} />
                                <p style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Execution queue is clear</p>
                                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: 6 }}>All AI actions are within envelope limits</p>
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                                {approvals.map(a => (
                                    <div key={a.id} className="animate-slide-up" style={{ padding: '1rem 1.1rem', borderRadius: 12, background: 'rgba(245,158,11,0.06)', border: '1px solid rgba(245,158,11,0.15)' }}>
                                        <div style={{ marginBottom: '0.75rem' }}>
                                            <span style={{ fontSize: '0.65rem', fontFamily: 'monospace', color: 'var(--text-muted)' }}>{a.id}</span>
                                            <p style={{ fontWeight: 600, fontSize: '0.92rem', color: 'var(--text-primary)', marginTop: 4 }}>{a.action}</p>
                                        </div>
                                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                                            <button className="btn-primary" onClick={() => decide(a.id, 'approve')} disabled={actioning === a.id}
                                                style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', padding: '0.4rem 1rem', flex: 1, justifyContent: 'center' }}>
                                                {actioning === a.id ? <Loader2 size={13} className="animate-spin" /> : <CheckCircle2 size={13} />} Approve
                                            </button>
                                            <button className="btn-ghost" onClick={() => decide(a.id, 'reject')} disabled={actioning === a.id}
                                                style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', padding: '0.4rem 1rem', flex: 1, justifyContent: 'center', color: 'var(--rose)' }}>
                                                <XCircle size={13} /> Reject
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Decision History */}
                    <div className="glass" style={{ padding: '1.5rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '1.25rem' }}>
                            <Shield size={16} color="var(--indigo)" />
                            <h2 style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Decision Log</h2>
                        </div>
                        {history.length === 0 ? (
                            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center', padding: '2rem 0' }}>No decisions yet this session</p>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                                {history.map((h, i) => (
                                    <div key={i} className="animate-slide-up" style={{ padding: '0.75rem', borderRadius: 8, background: 'rgba(255,255,255,0.02)' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 4 }}>
                                            <span className={`badge ${h.decision === 'approve' ? 'badge-success' : 'badge-danger'}`}>{h.decision}</span>
                                            <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>{h.at}</span>
                                        </div>
                                        <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{h.action}</p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </main>
        </div>
    );
}
