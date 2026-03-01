"use client";

import React, { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { useCompanyStore } from "@/store/companyStore";
import { Plug, Zap, CheckCircle2, XCircle, ShieldCheck } from "lucide-react";
import axios from "axios";

export default function PlatformConnectionsPage() {
    const params = useParams();
    const companyId = Array.isArray(params.companyId) ? params.companyId[0] : params.companyId || "default";

    const { platforms, fetchPlatforms } = useCompanyStore();
    const [authLoading, setAuthLoading] = useState<string | null>(null);

    useEffect(() => {
        if (companyId) {
            fetchPlatforms(companyId);
        }
    }, [companyId, fetchPlatforms]);

    const handleOAuthFlow = async (platformName: string) => {
        setAuthLoading(platformName);
        try {
            // Reaches out to the `marketing_ai/app/api/connectors.py` routes we built!
            const res = await axios.get(`http://localhost:8000/api/v1/connectors/${platformName}/login?company_id=${companyId}`);
            if (res.data.authorization_url) {
                // Redirect user to Meta/Google/TikTok OAuth portal
                window.location.href = res.data.authorization_url;
            }
        } catch (e) {
            console.error(e);
            alert(`Failed to initialize ${platformName} OAuth. Make sure FastAPI is running. `);
        } finally {
            setAuthLoading(null);
        }
    };

    // Pre-declare our supported visual platforms 
    const PLATFORM_UI_DEFS = [
        { key: 'meta', label: 'Meta Ads Manager', iconColor: 'text-blue-600', bgIcon: 'bg-blue-50' },
        { key: 'google', label: 'Google Ads', iconColor: 'text-red-500', bgIcon: 'bg-red-50' },
        { key: 'tiktok', label: 'TikTok For Business', iconColor: 'text-slate-900', bgIcon: 'bg-slate-100' },
        { key: 'linkedin', label: 'LinkedIn Ads', iconColor: 'text-sky-600', bgIcon: 'bg-sky-50' },
        { key: 'twitter', label: 'X (Twitter)', iconColor: 'text-slate-900', bgIcon: 'bg-slate-100' },
        { key: 'reddit', label: 'Reddit Ads', iconColor: 'text-orange-500', bgIcon: 'bg-orange-50' }
    ];

    return (
        <div className="p-8 lg:p-12 min-h-screen bg-slate-50 text-slate-800">
            <header className="mb-10 pb-6 border-b border-slate-200">
                <h1 className="text-4xl font-extrabold text-slate-900 mb-2">Connect Advertising Platforms</h1>
                <p className="text-slate-500 max-w-2xl">
                    Securely authenticate via OAuth 2.0 to sync metrics, engagement, and campaign spend directly matching the Company vector model.
                    Keys are safely stored via symmetric Fernet AES encryption in the Qdrant & PostgreSQL databases.
                </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl">
                {PLATFORM_UI_DEFS.map((def) => {
                    // Check if connected from Zustand Store
                    const pState = platforms.find(p => p.platform === def.key);
                    const isConnected = pState?.status === 'connected';

                    return (
                        <div key={def.key} className={`bg-white border rounded-2xl p-6 shadow-sm transition transform hover:-translate-y-1 ${isConnected ? 'border-emerald-200' : 'border-slate-200'}`}>
                            <div className="flex items-start justify-between mb-8">
                                <div className={`p-4 rounded-2xl ${def.bgIcon} ${def.iconColor} border border-slate-100 shadow-sm`}>
                                    <Plug size={32} />
                                </div>
                                {isConnected ? (
                                    <div className="text-emerald-600 flex items-center gap-1 font-bold text-sm bg-emerald-50 px-3 py-1 rounded-full border border-emerald-100">
                                        <CheckCircle2 size={16} /> CONNECTED
                                    </div>
                                ) : (
                                    <div className="text-slate-400 flex items-center gap-1 font-semibold text-sm bg-slate-100 px-3 py-1 rounded-full">
                                        <XCircle size={16} /> PENDING
                                    </div>
                                )}
                            </div>

                            <h3 className="text-xl font-bold text-slate-800 mb-1">{def.label}</h3>
                            <p className="text-slate-500 text-sm mb-6 h-10">
                                {isConnected
                                    ? `Last synced: ${pState?.lastSync || 'Just now'} via AES Auth.`
                                    : `Authenticate safely to allow AI Orchestrator spend mapping.`
                                }
                            </p>

                            <button
                                onClick={() => handleOAuthFlow(def.key)}
                                disabled={authLoading === def.key || isConnected}
                                className={`w-full py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition 
                                        ${isConnected
                                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                                        : 'bg-indigo-600 text-white hover:bg-indigo-700 shadow-md'
                                    }`}
                            >
                                {authLoading === def.key ? (
                                    <span className="animate-pulse">Opening Portal...</span>
                                ) : isConnected ? (
                                    <><ShieldCheck size={20} /> Verified</>
                                ) : (
                                    <><Zap size={20} /> Connect OAuth</>
                                )}
                            </button>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
