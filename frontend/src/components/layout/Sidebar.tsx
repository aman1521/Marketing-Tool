'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard, Building2, Cpu, FlaskConical,
    Search, Shield, LogOut, Brain, ChevronRight
} from 'lucide-react';

const NAV = [
    { href: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { href: '/companies', icon: Building2, label: 'Companies' },
    { href: '/automation', icon: Shield, label: 'Automation' },
    { href: '/competitor', icon: Search, label: 'Competitor AI' },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside style={{
            width: 220, minHeight: '100vh',
            background: 'var(--bg-card)',
            borderRight: '1px solid var(--border)',
            display: 'flex', flexDirection: 'column',
            position: 'fixed', left: 0, top: 0, zIndex: 50,
        }}>
            {/* Logo */}
            <div style={{ padding: '1.25rem 1rem 1rem', borderBottom: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <div style={{
                        width: 34, height: 34, borderRadius: 10,
                        background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        boxShadow: '0 4px 16px rgba(99,102,241,0.4)'
                    }}>
                        <Brain size={18} color="white" />
                    </div>
                    <div>
                        <p style={{ fontWeight: 800, fontSize: '0.85rem', color: 'var(--text-primary)', lineHeight: 1 }}>Marketing OS</p>
                        <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 2 }}>Intelligence Core</p>
                    </div>
                </div>
            </div>

            {/* Nav */}
            <nav style={{ flex: 1, padding: '0.75rem 0.5rem', display: 'flex', flexDirection: 'column', gap: '2px' }}>
                {NAV.map(({ href, icon: Icon, label }) => (
                    <Link
                        key={href}
                        href={href}
                        className={`sidebar-item ${pathname.startsWith(href) ? 'active' : ''}`}
                    >
                        <Icon size={16} />
                        {label}
                        {pathname.startsWith(href) && (
                            <ChevronRight size={12} style={{ marginLeft: 'auto', opacity: 0.5 }} />
                        )}
                    </Link>
                ))}
            </nav>

            {/* Footer */}
            <div style={{ padding: '0.75rem 0.75rem 1rem', borderTop: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', padding: '0.5rem', borderRadius: 10, background: 'rgba(255,255,255,0.03)' }}>
                    <div style={{ width: 30, height: 30, borderRadius: '50%', background: 'linear-gradient(135deg,#6366f1,#8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.7rem', fontWeight: 700, color: 'white' }}>
                        OP
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                        <p style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-primary)', truncate: true }}>Operator</p>
                        <p style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>alpha access</p>
                    </div>
                    <button style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-muted)', padding: 4 }} title="Logout"
                        onClick={() => { localStorage.removeItem('token'); window.location.href = '/login'; }}>
                        <LogOut size={14} />
                    </button>
                </div>
            </div>
        </aside>
    );
}
