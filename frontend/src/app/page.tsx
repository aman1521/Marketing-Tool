import Link from 'next/link';
import { ArrowRight, BarChart3, Workflow, ShieldCheck } from 'lucide-react';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50 text-slate-800 p-8">
      <div className="max-w-3xl text-center space-y-8">
        <h1 className="text-5xl font-extrabold tracking-tight text-slate-900 leading-tight">
          AI Marketing Intelligence <br />
          <span className="text-indigo-600">Autonomous SaaS</span>
        </h1>

        <p className="text-xl text-slate-600 leading-relaxed max-w-2xl mx-auto">
          Scale your advertising natively across Meta, Google, TikTok, LinkedIn, Twitter, and Reddit
          simultaneously using autonomous strategy engines.
        </p>

        <div className="flex justify-center gap-6 pt-4">
          <Link href="/dashboard" className="bg-indigo-600 text-white hover:bg-indigo-700 px-8 py-4 rounded-xl flex shadow-lg hover:shadow-indigo-500/30 transition transform hover:-translate-y-1 font-semibold items-center gap-2">
            Enter Dashboard <ArrowRight size={20} />
          </Link>
          <Link href="/companies" className="bg-white text-slate-700 hover:text-slate-900 px-8 py-4 rounded-xl flex shadow-md hover:shadow-lg border border-slate-200 transition font-semibold items-center">
            View Companies
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl w-full mt-24">

        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center text-center hover:border-indigo-100 transition">
          <div className="h-14 w-14 bg-indigo-50 flex items-center justify-center rounded-2xl mb-6">
            <Workflow size={28} className="text-indigo-600" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">Multi-Platform Automation</h3>
          <p className="text-slate-500">Cross-communicate insights between Social and Ad platforms instantly via intelligent APIs.</p>
        </div>

        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center text-center hover:border-emerald-100 transition">
          <div className="h-14 w-14 bg-emerald-50 flex items-center justify-center rounded-2xl mb-6">
            <ShieldCheck size={28} className="text-emerald-600" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">AI Safety Limits</h3>
          <p className="text-slate-500">Built-in hard limits (like 30% max budget shift) prevent destructive runaway AI behaviors.</p>
        </div>

        <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 flex flex-col items-center text-center hover:border-blue-100 transition">
          <div className="h-14 w-14 bg-blue-50 flex items-center justify-center rounded-2xl mb-6">
            <BarChart3 size={28} className="text-blue-600" />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">Aggregated Analytics</h3>
          <p className="text-slate-500">See normalized ROAS, Spend, and Engagement across all 6 connector platforms.</p>
        </div>

      </div>
    </div>
  );
}
