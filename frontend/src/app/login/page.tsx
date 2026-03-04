'use client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '@/lib/api';
import { Brain, Loader2, Eye, EyeOff } from 'lucide-react';

export default function LoginPage() {
    const router = useRouter();
    const [tab, setTab] = useState<'login' | 'register'>('login');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [name, setName] = useState('');
    const [showPw, setShowPw] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const submit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            if (tab === 'login') {
                const res = await authAPI.login(email, password);
                const token = res.data?.access_token || res.data?.token || 'mocked_token';
                localStorage.setItem('token', token);
            } else {
                await authAPI.register(email, password, name);
                const res = await authAPI.login(email, password);
                const token = res.data?.access_token || res.data?.token || 'mocked_token';
                localStorage.setItem('token', token);
            }
            router.push('/dashboard');
        } catch (err: any) {
            setError(err?.response?.data?.detail || 'Authentication failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
            background: 'var(--bg-base)',
            backgroundImage: 'radial-gradient(ellipse 80% 60% at 50% -10%, rgba(99,102,241,0.12) 0%, transparent 70%)'
        }}>
            <div className="animate-slide-up" style={{ width: '100%', maxWidth: 420, padding: '0 1rem' }}>

                {/* Logo */}
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <div style={{
                        width: 56, height: 56, borderRadius: 16, margin: '0 auto 1rem',
                        background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        boxShadow: '0 8px 32px rgba(99,102,241,0.4)'
                    }}>
                        <Brain size={28} color="white" />
                    </div>
                    <h1 style={{ fontWeight: 800, fontSize: '1.5rem', color: 'var(--text-primary)' }}>Marketing OS</h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 4 }}>Autonomous Intelligence Platform</p>
                </div>

                {/* Card */}
                <div className="glass" style={{ padding: '2rem' }}>
                    {/* Tabs */}
                    <div style={{ display: 'flex', gap: '4px', background: 'rgba(255,255,255,0.04)', borderRadius: 10, padding: 4, marginBottom: '1.5rem' }}>
                        {(['login', 'register'] as const).map(t => (
                            <button key={t} onClick={() => setTab(t)} style={{
                                flex: 1, border: 'none', cursor: 'pointer', borderRadius: 8,
                                padding: '0.5rem', fontWeight: 600, fontSize: '0.85rem', transition: 'all 0.2s',
                                background: tab === t ? 'linear-gradient(135deg,#6366f1,#8b5cf6)' : 'transparent',
                                color: tab === t ? 'white' : 'var(--text-secondary)',
                                boxShadow: tab === t ? '0 2px 12px rgba(99,102,241,0.4)' : 'none'
                            }}>
                                {t === 'login' ? 'Sign In' : 'Register'}
                            </button>
                        ))}
                    </div>

                    <form onSubmit={submit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                        {tab === 'register' && (
                            <div>
                                <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: 6 }}>FULL NAME</label>
                                <input className="input-dark" type="text" value={name} onChange={e => setName(e.target.value)} placeholder="Jane Smith" required />
                            </div>
                        )}
                        <div>
                            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: 6 }}>EMAIL</label>
                            <input className="input-dark" type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="operator@company.com" required />
                        </div>
                        <div>
                            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: 600, display: 'block', marginBottom: 6 }}>PASSWORD</label>
                            <div style={{ position: 'relative' }}>
                                <input className="input-dark" type={showPw ? 'text' : 'password'} value={password} onChange={e => setPassword(e.target.value)} placeholder="••••••••" required style={{ paddingRight: '2.5rem' }} />
                                <button type="button" onClick={() => setShowPw(!showPw)} style={{ position: 'absolute', right: '0.75rem', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: 0 }}>
                                    {showPw ? <EyeOff size={16} /> : <Eye size={16} />}
                                </button>
                            </div>
                        </div>

                        {error && (
                            <div style={{ background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.2)', borderRadius: 8, padding: '0.65rem 0.9rem', fontSize: '0.8rem', color: '#fb7185' }}>
                                {error}
                            </div>
                        )}

                        <button className="btn-primary" type="submit" disabled={loading} style={{ marginTop: '0.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                            {loading ? <><Loader2 size={16} className="animate-spin" /> Processing…</> : (tab === 'login' ? 'Sign In' : 'Create Account')}
                        </button>
                    </form>
                </div>

                <p style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '1.5rem' }}>
                    Marketing OS Alpha · Internal Operator Access Only
                </p>
            </div>
        </div>
    );
}
