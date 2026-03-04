'use client';
import { useState } from 'react';
import Sidebar from '@/components/layout/Sidebar';
import { competitorAPI } from '@/lib/api';
import { Search, Loader2, Brain, TrendingUp, Globe, FileText } from 'lucide-react';

export default function CompetitorPage() {
    const [url, setUrl] = useState('');
    const [companyName, setCompanyName] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState('');

    const analyze = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!url || !companyName) return;
        setLoading(true); setError(''); setResult(null);
        try {
            const res = await competitorAPI.analyze(url, companyName);
            setResult(res.data);
        } catch (err: any) {
            setError(err?.response?.data?.detail || 'Analysis failed. Check the URL and try again.');
        } finally { setLoading(false); }
    };

    return (
        <div style={{ display: 'flex' }}>
            <Sidebar />
            <main style={{ marginLeft: 220, flex: 1, minHeight: '100vh', padding: '2rem', background: 'var(--bg-base)' }}>
                <div style={{ marginBottom: '2rem' }}>
                    <h1 style={{ fontWeight: 800, fontSize: '1.5rem' }}><span className="gradient-text">Competitor AI</span></h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', marginTop: 4 }}>
                        Crawl competitor websites and generate strategic gap analysis using Claude
                    </p>
                </div>

                {/* Input Card */}
                <div className="glass" style={{ padding: '1.75rem', maxWidth: 680, marginBottom: '1.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '1.25rem' }}>
                        <Search size={16} color="var(--cyan)" />
                        <h2 style={{ fontWeight: 700, fontSize: '0.85rem', color: 'var(--text-primary)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Analyze Competitor</h2>
                    </div>
                    <form onSubmit={analyze} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        <div>
                            <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', display: 'block', marginBottom: 6, textTransform: 'uppercase' }}>Your Company Name</label>
                            <input className="input-dark" value={companyName} onChange={e => setCompanyName(e.target.value)} placeholder="Acme Corp" required />
                        </div>
                        <div>
                            <label style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', display: 'block', marginBottom: 6, textTransform: 'uppercase' }}>Competitor URL</label>
                            <input className="input-dark" value={url} onChange={e => setUrl(e.target.value)} placeholder="https://competitor.com" type="url" required />
                        </div>
                        {error && (
                            <div style={{ background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.2)', borderRadius: 8, padding: '0.75rem', fontSize: '0.8rem', color: '#fb7185' }}>
                                {error}
                            </div>
                        )}
                        <button className="btn-primary" type="submit" disabled={loading} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, marginTop: 4 }}>
                            {loading ? <><Loader2 size={14} className="animate-spin" /> Analyzing (this may take 30–60s)…</> : <><Brain size={14} /> Run AI Gap Analysis</>}
                        </button>
                    </form>
                </div>

                {/* Loading State */}
                {loading && (
                    <div className="glass animate-slide-up" style={{ padding: '2rem', maxWidth: 680 }}>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            {['Crawling competitor website…', 'Cleaning and chunking content…', 'Running Claude strategic analysis…', 'Generating gap report…'].map((step, i) => (
                                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, color: 'var(--text-secondary)', fontSize: '0.82rem' }}>
                                    <Loader2 size={13} color="var(--indigo)" className="animate-spin" />
                                    {step}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Results */}
                {result && (
                    <div className="animate-slide-up" style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxWidth: 860 }}>
                        {/* Summary Stats */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
                            {[
                                { icon: Globe, label: 'Pages Scraped', value: result.pages_scraped?.length ?? 0, color: 'cyan' },
                                { icon: FileText, label: 'Chunks Processed', value: result.total_chunks_processed ?? 0, color: 'violet' },
                                { icon: TrendingUp, label: 'Analysis Status', value: result.status ?? 'Done', color: 'emerald' },
                            ].map(({ icon: Icon, label, value, color }) => (
                                <div key={label} className="glass" style={{ padding: '1.1rem', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                                    <div style={{ width: 36, height: 36, borderRadius: 8, background: `rgba(99,102,241,0.12)`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                        <Icon size={18} color="var(--indigo)" />
                                    </div>
                                    <div>
                                        <p style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', fontWeight: 700 }}>{label}</p>
                                        <p style={{ fontWeight: 800, fontSize: '1.1rem', color: 'var(--text-primary)' }}>{value}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Gap Report */}
                        {result.gap_analysis && (
                            <div className="glass" style={{ padding: '1.75rem' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '1.25rem' }}>
                                    <Brain size={16} color="var(--violet)" />
                                    <h2 style={{ fontWeight: 700, fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Strategic Gap Report</h2>
                                    <span className="badge badge-indigo" style={{ marginLeft: 'auto' }}>Claude Analysis</span>
                                </div>
                                <div style={{
                                    fontFamily: 'Inter, sans-serif', fontSize: '0.85rem', lineHeight: 1.75,
                                    color: 'var(--text-secondary)',
                                    background: 'rgba(255,255,255,0.02)', borderRadius: 10, padding: '1.25rem',
                                    whiteSpace: 'pre-wrap', maxHeight: 600, overflowY: 'auto'
                                }}>
                                    {result.gap_analysis}
                                </div>
                            </div>
                        )}

                        {/* Pages */}
                        {result.pages_scraped?.length > 0 && (
                            <div className="glass" style={{ padding: '1.25rem' }}>
                                <p style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '0.75rem' }}>Pages Crawled</p>
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                                    {result.pages_scraped.map((p: string) => (
                                        <span key={p} style={{ fontSize: '0.72rem', padding: '3px 10px', background: 'rgba(255,255,255,0.05)', borderRadius: 20, color: 'var(--text-muted)', fontFamily: 'monospace' }}>{p}</span>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}
            </main>
        </div>
    );
}
