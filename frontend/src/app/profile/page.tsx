"use client";

import React, { useState } from "react";
import { Check, Zap, Server } from "lucide-react";
import axios from "axios";

export default function PricingPage() {
    const [isLoading, setIsLoading] = useState<string | null>(null);

    const handleSubscribe = async (priceId: string, planName: string) => {
        setIsLoading(planName);
        try {
            // Assumes JWT handling is done globally in an Axios interceptor 
            // Send the mock price_id to FastAPI Route that returns a Stripe Checkout URL
            const res = await axios.post(`http://localhost:8000/api/v1/subscriptions/checkout?price_id=${priceId}`);
            if (res.data.url) {
                window.location.href = res.data.url;
            }
        } catch (err) {
            console.error("Failed to checkout:", err);
            alert("Checkout failed. Check server logs.");
        } finally {
            setIsLoading(null);
        }
    };

    return (
        <div className="p-8 lg:p-12 min-h-screen">
            <div className="max-w-3xl mx-auto text-center mb-16">
                <h1 className="text-4xl font-extrabold text-slate-900 mb-4">Autonomous Marketing Pricing</h1>
                <p className="text-lg text-slate-500">Simple, transparent pricing to scale your multi-platform advertising intelligence securely.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
                {/* Basic / Solopreneur Plan */}
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
                    <h2 className="text-xl font-bold text-slate-800 mb-2">Solopreneur</h2>
                    <div className="text-slate-500 mb-6 font-medium">1 Brand Connection</div>
                    <div className="text-4xl font-extrabold text-slate-900 mb-6">$49<span className="text-lg font-medium text-slate-400">/mo</span></div>
                    <ul className="space-y-4 mb-8">
                        <li className="flex items-center gap-3 text-slate-600"><Check className="text-emerald-500" size={20} /> Connect Meta & Google</li>
                        <li className="flex items-center gap-3 text-slate-600"><Check className="text-emerald-500" size={20} /> Basic Campaign Syncing</li>
                        <li className="flex items-center gap-3 text-slate-600"><Check className="text-emerald-500" size={20} /> 5 AI Strategy Runs / week</li>
                        <li className="flex items-center gap-3 text-slate-400">No Auto-Mode</li>
                    </ul>
                    <button
                        onClick={() => handleSubscribe('price_solo_123', 'solo')}
                        disabled={!!isLoading}
                        className="w-full bg-slate-50 text-slate-900 border border-slate-300 font-semibold py-3 rounded-xl hover:bg-slate-100 transition"
                    >
                        {isLoading === 'solo' ? 'Connecting...' : 'Start Free Trial'}
                    </button>
                </div>

                {/* Growth / Professional Plan */}
                <div className="bg-indigo-600 p-8 rounded-2xl shadow-xl shadow-indigo-600/20 border-2 border-indigo-400 relative transform md:-translate-y-4">
                    <div className="absolute top-0 right-1/2 translate-x-1/2 -translate-y-1/2 bg-indigo-200 text-indigo-900 font-bold px-4 py-1 rounded-full text-sm">
                        MOST POPULAR
                    </div>
                    <h2 className="text-xl font-bold text-white mb-2">Professional SaaS</h2>
                    <div className="text-indigo-200 mb-6 font-medium">3 Brand Connections</div>
                    <div className="text-4xl font-extrabold text-white mb-6">$199<span className="text-lg font-medium text-indigo-300">/mo</span></div>
                    <ul className="space-y-4 mb-8 text-indigo-100">
                        <li className="flex items-center gap-3"><Check className="text-emerald-400" size={20} /> Connect All 6 Platforms</li>
                        <li className="flex items-center gap-3"><Check className="text-emerald-400" size={20} /> Competitor Vector Tracking</li>
                        <li className="flex items-center gap-3"><Check className="text-emerald-400" size={20} /> Unlimited AI Strategies</li>
                        <li className="flex items-center gap-3"><Zap className="text-amber-400" size={20} /> Enable Safe Auto-Mode</li>
                    </ul>
                    <button
                        onClick={() => handleSubscribe('price_pro_456', 'pro')}
                        disabled={!!isLoading}
                        className="w-full bg-white text-indigo-600 font-bold py-3 rounded-xl hover:bg-indigo-50 transition shadow-sm"
                    >
                        {isLoading === 'pro' ? 'Connecting...' : 'Upgrade Limit'}
                    </button>
                </div>

                {/* Agency Plan */}
                <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-200">
                    <h2 className="text-xl font-bold text-slate-800 mb-2">Agency</h2>
                    <div className="text-slate-500 mb-6 font-medium">Unlimited Brands</div>
                    <div className="text-4xl font-extrabold text-slate-900 mb-6">$999<span className="text-lg font-medium text-slate-400">/mo</span></div>
                    <ul className="space-y-4 mb-8">
                        <li className="flex items-center gap-3 text-slate-600"><Check className="text-emerald-500" size={20} /> Everything in Pro</li>
                        <li className="flex items-center gap-3 text-slate-600"><Check className="text-emerald-500" size={20} /> Advanced AirLLM Tagging</li>
                        <li className="flex items-center gap-3 text-slate-600"><Check className="text-emerald-500" size={20} /> Custom Budget Risk Rules</li>
                        <li className="flex items-center gap-3 text-slate-600"><Server className="text-emerald-500" size={20} /> Dedicated Priority Support</li>
                    </ul>
                    <button
                        onClick={() => handleSubscribe('price_agency_789', 'agency')}
                        disabled={!!isLoading}
                        className="w-full bg-slate-50 text-slate-900 border border-slate-300 font-semibold py-3 rounded-xl hover:bg-slate-100 transition"
                    >
                        {isLoading === 'agency' ? 'Connecting...' : 'Contact Sales'}
                    </button>
                </div>
            </div>
        </div>
    )
}
