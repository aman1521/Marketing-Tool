"use client";

import React, { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useCompanyStore } from "@/store/companyStore";
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { ToggleRight, ToggleLeft, Edit, AlertTriangle, Plus } from "lucide-react";

export default function PlatformAssetPage() {
    const params = useParams();
    const companyId = Array.isArray(params.companyId) ? params.companyId[0] : params.companyId || "default";
    const platform = Array.isArray(params.platform) ? params.platform[0] : params.platform || "meta";

    const { fetchAssets, campaigns, posts, isLoading, updateCampaignBudget, toggleAutomation, proposeStrategy } = useCompanyStore();

    // UI state
    const [aiInsight, setAiInsight] = useState<Record<string, unknown> | null>(null);

    useEffect(() => {
        if (companyId && platform) {
            fetchAssets(companyId, platform);
        }
    }, [companyId, platform, fetchAssets]);

    const isAdsPlatform = ['meta', 'google', 'linkedin'].includes(platform.toLowerCase());
    const isSocialPlatform = ['twitter', 'tiktok', 'reddit'].includes(platform.toLowerCase());

    const handleAITest = async () => {
        const strats = await proposeStrategy(companyId, "Moderate");
        if (strats.length > 0) setAiInsight(strats[0]);
    };

    const mockChartData = [
        { name: 'Mon', spend: 40, cpc: 0.8 },
        { name: 'Tue', spend: 30, cpc: 0.8 },
        { name: 'Wed', spend: 20, cpc: 0.75 },
        { name: 'Thu', spend: 50, cpc: 0.9 },
        { name: 'Fri', spend: 45, cpc: 0.82 },
        { name: 'Sat', spend: 60, cpc: 1.1 },
        { name: 'Sun', spend: 75, cpc: 1.2 },
    ];

    if (isLoading) return <div className="p-8"><div className="animate-pulse bg-slate-200 h-10 w-48 rounded mb-6"></div></div>;

    return (
        <div className="p-8 space-y-8 bg-gray-50 min-h-screen text-slate-800">
            {/* Header */}
            <header className="flex justify-between items-center bg-white p-6 rounded-xl shadow-sm border border-slate-100">
                <div>
                    <h1 className="text-3xl font-bold capitalize text-slate-900">{platform} Manager</h1>
                    <p className="text-slate-500 mt-1">Managing intelligence and automation for {platform}.</p>
                </div>
                <div className="flex gap-4">
                    <button
                        onClick={handleAITest}
                        className="bg-indigo-600 hover:bg-indigo-700 transition flex items-center gap-2 text-white font-medium px-5 py-2.5 rounded-lg shadow-sm"
                    >
                        <AlertTriangle size={18} /> Run AI Evaluation
                    </button>
                    {isSocialPlatform && (
                        <button className="bg-emerald-500 hover:bg-emerald-600 transition flex items-center gap-2 text-white font-medium px-5 py-2.5 rounded-lg shadow-sm">
                            <Plus size={18} /> New AI Post
                        </button>
                    )}
                </div>
            </header>

            {/* AI Insight Overlay */}
            {aiInsight && (
                <div className="bg-amber-50 border-l-4 border-amber-500 p-6 rounded-r-xl shadow-sm flex flex-col items-start gap-4">
                    <div className="flex items-center gap-3">
                        <AlertTriangle className="text-amber-500" size={24} />
                        <h3 className="font-bold text-lg text-amber-900">Safety Engine: Proposed Strategy - Confidence {((aiInsight as Record<string, number>).confidence_score * 100).toFixed(0)}%</h3>
                    </div>
                    <p className="text-amber-800 italic">&quot;{(aiInsight as Record<string, string>).reasoning_text}&quot;</p>
                    <div className="bg-white p-3 rounded shadow-sm w-full md:w-auto">
                        <span className="text-sm font-semibold text-slate-500 uppercase tracking-wider">Action: </span>
                        <span className="font-mono text-slate-800 ml-2">{(aiInsight as Record<string, string>).action_type}</span>
                    </div>
                    {(aiInsight as Record<string, boolean>).requires_approval ? (
                        <button className="bg-amber-600 text-white px-6 py-2 rounded shadow-sm font-medium hover:bg-amber-700 transition">
                            Approve Action Override
                        </button>
                    ) : (
                        <span className="text-emerald-600 font-bold bg-emerald-50 px-3 py-1 rounded">Safely Auto-Executed</span>
                    )}
                </div>
            )}

            {isAdsPlatform && (
                <>
                    {/* Charts */}
                    <section className="bg-white shadow-sm border border-slate-100 rounded-xl p-6 h-80">
                        <h2 className="text-lg font-bold mb-4 text-slate-800">Performance Overview (7 Day)</h2>
                        <ResponsiveContainer width="100%" height="85%">
                            <LineChart data={mockChartData}>
                                <CartesianGrid strokeDasharray="3 3" opacity={0.5} />
                                <XAxis dataKey="name" stroke="#94a3b8" />
                                <YAxis yAxisId="left" stroke="#8b5cf6" />
                                <YAxis yAxisId="right" orientation="right" stroke="#10b981" />
                                <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                <Legend />
                                <Line yAxisId="left" type="monotone" dataKey="spend" stroke="#8b5cf6" strokeWidth={3} activeDot={{ r: 8 }} />
                                <Line yAxisId="right" type="monotone" dataKey="cpc" stroke="#10b981" strokeWidth={3} />
                            </LineChart>
                        </ResponsiveContainer>
                    </section>

                    {/* Campaigns Table */}
                    <section className="bg-white shadow-sm border border-slate-100 rounded-xl overflow-hidden">
                        <div className="p-6 border-b border-slate-100 bg-slate-50/50">
                            <h2 className="text-lg font-bold text-slate-800">Active Campaigns</h2>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="w-full text-left">
                                <thead className="bg-slate-50 text-slate-500 uppercase text-xs font-semibold">
                                    <tr>
                                        <th className="px-6 py-4">Campaign Name</th>
                                        <th className="px-6 py-4">Status</th>
                                        <th className="px-6 py-4">Daily Budget</th>
                                        <th className="px-6 py-4">Spend (YTD)</th>
                                        <th className="px-6 py-4">Automation</th>
                                        <th className="px-6 py-4 text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {campaigns.map((camp) => (
                                        <tr key={camp.id} className="hover:bg-slate-50/50 transition">
                                            <td className="px-6 py-4 font-medium text-slate-800">{camp.name}</td>
                                            <td className="px-6 py-4">
                                                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${camp.status === 'active' ? 'bg-emerald-100 text-emerald-700' : 'bg-slate-100 text-slate-600'}`}>
                                                    {camp.status}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4 text-slate-700 font-mono">${camp.dailyBudget.toFixed(2)}</td>
                                            <td className="px-6 py-4 text-slate-700 font-mono">${camp.performanceMetrics.spend.toFixed(2)}</td>
                                            <td className="px-6 py-4">
                                                <button onClick={() => toggleAutomation(companyId, camp.id, !camp.isAutoManaged)} className="focus:outline-none" title="Toggle Automation">
                                                    {camp.isAutoManaged ? (
                                                        <ToggleRight size={32} className="text-indigo-600" />
                                                    ) : (
                                                        <ToggleLeft size={32} className="text-slate-300" />
                                                    )}
                                                </button>
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <button
                                                    onClick={() => updateCampaignBudget(companyId, camp.id, camp.dailyBudget + 50)}
                                                    className="p-2 hover:bg-slate-100 rounded-full transition text-slate-500 hover:text-indigo-600"
                                                    title="Edit Budget"
                                                >
                                                    <Edit size={18} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </section>
                </>
            )}

            {isSocialPlatform && (
                <section className="bg-white shadow-sm border border-slate-100 rounded-xl overflow-hidden">
                    <div className="p-6 border-b border-slate-100 bg-slate-50/50">
                        <h2 className="text-lg font-bold text-slate-800">Content Schedule</h2>
                    </div>
                    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                        {posts.map(post => (
                            <div key={post.id} className="border border-slate-200 p-4 rounded-lg bg-white shadow-sm hover:shadow transition">
                                <div className="flex justify-between items-start mb-3">
                                    <span className="text-xs font-bold uppercase text-emerald-600 bg-emerald-50 px-2 py-1 rounded">{post.status}</span>
                                    {post.engagementMetrics.likes > 0 && <span className="text-xs text-slate-500 font-mono">❤ {post.engagementMetrics.likes}</span>}
                                </div>
                                <p className="text-slate-800 leading-relaxed font-medium">&quot;{post.content}&quot;</p>
                            </div>
                        ))}
                    </div>
                </section>
            )}
        </div>
    );
}

