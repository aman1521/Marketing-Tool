import Link from 'next/link';
import { ArrowRight, Brain, Zap, ShieldCheck, BarChart3, Search, CpuIcon } from 'lucide-react';

export default function Home() {
  return (
    <div style={{
      minHeight: '100vh', background: 'var(--bg-base)', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem',
      backgroundImage: 'radial-gradient(ellipse 80% 50% at 50% -5%, rgba(99,102,241,0.14) 0%, transparent 70%)'
    }}>
      {/* Hero */}
      <div style={{ textAlign: 'center', maxWidth: 640, marginBottom: '4rem' }} className="animate-slide-up">
        <div style={{
          width: 64, height: 64, borderRadius: 18, margin: '0 auto 1.5rem',
          background: 'linear-gradient(135deg,#6366f1,#8b5cf6)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 12px 40px rgba(99,102,241,0.45)'
        }}>
          <Brain size={30} color="white" />
        </div>

        <h1 style={{ fontSize: '3rem', fontWeight: 900, lineHeight: 1.1, marginBottom: '1.25rem' }}>
          <span className="gradient-text">Autonomous</span> Marketing<br />Intelligence OS
        </h1>

        <p style={{ fontSize: '1.05rem', color: 'var(--text-secondary)', lineHeight: 1.7, marginBottom: '2rem' }}>
          Multi-tenant AI that scales campaigns across Meta, Google, TikTok, LinkedIn, Twitter and Reddit —
          autonomously, within your defined envelopes.
        </p>

        <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center', flexWrap: 'wrap' }}>
          <Link href="/login" className="btn-primary" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: '0.95rem', padding: '0.8rem 1.75rem' }}>
            Enter Platform <ArrowRight size={18} />
          </Link>
          <Link href="/dashboard" className="btn-ghost" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, fontSize: '0.95rem', padding: '0.8rem 1.75rem' }}>
            View Dashboard
          </Link>
        </div>
      </div>

      {/* Feature Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))', gap: '1rem', maxWidth: 900, width: '100%' }}>
        {[
          { icon: Zap, title: 'Autonomous Execution', desc: 'AI executes budget shifts, pauses, and scaling decisions within your defined envelope limits.', color: 'indigo' },
          { icon: ShieldCheck, title: 'Envelope Governance', desc: 'Genesis layer enforces hard limits — max 30% budget shifts, automated rollback on drift.', color: 'emerald' },
          { icon: BarChart3, title: 'Multi-Platform ROI', desc: 'Normalized ROAS, spend, and engagement tracked across all 6 ad platforms simultaneously.', color: 'cyan' },
          { icon: Brain, title: 'Compounding Intelligence', desc: 'Strategy archetypes compound over time — high-confidence patterns bias future AI decisions.', color: 'violet' },
          { icon: Search, title: 'Competitor AI', desc: 'Crawl competitor sites, chunk content, and generate Claude-powered strategic gap reports.', color: 'amber' },
          { icon: CpuIcon, title: 'Decision Speed Index', desc: 'Track the end-to-end velocity of the AI decision loop and identify human approval bottlenecks.', color: 'rose' },
        ].map(({ icon: Icon, title, desc, color }) => {
          const bg: Record<string, string> = { indigo: 'rgba(99,102,241,0.1)', emerald: 'rgba(16,185,129,0.1)', cyan: 'rgba(6,182,212,0.1)', violet: 'rgba(139,92,246,0.1)', amber: 'rgba(245,158,11,0.1)', rose: 'rgba(244,63,94,0.1)' };
          const ic: Record<string, string> = { indigo: '#818cf8', emerald: '#34d399', cyan: '#22d3ee', violet: '#c084fc', amber: '#fbbf24', rose: '#fb7185' };
          return (
            <div key={title} className="glass glass-hover" style={{ padding: '1.5rem' }}>
              <div style={{ width: 40, height: 40, borderRadius: 10, background: bg[color], display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '0.9rem' }}>
                <Icon size={20} color={ic[color]} />
              </div>
              <h3 style={{ fontWeight: 700, fontSize: '0.92rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>{title}</h3>
              <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>{desc}</p>
            </div>
          );
        })}
      </div>

      <p style={{ color: 'var(--text-muted)', fontSize: '0.72rem', marginTop: '3rem' }}>
        Internal Operator Access Only · Marketing OS Alpha ·{' '}
        <Link href="/login" style={{ color: 'var(--indigo)', textDecoration: 'none' }}>Sign In</Link>
      </p>
    </div>
  );
}
