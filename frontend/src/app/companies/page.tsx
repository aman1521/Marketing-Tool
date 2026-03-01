"use client";

import React from "react";
import { ShieldCheck, Plus, ArrowRight, Share2, Building2 } from "lucide-react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";

export default function CompaniesDashboard() {
    const router = useRouter();

    // In a real app we'd fetch these from the zustand store -> FastAPI GET /companies
    const mockCompanies = [
        { id: '123_demo', name: 'Acme Corp', industry: 'E-commerce', conn_count: 3, riskLevel: 'Aggressive' },
        { id: '456_demo', name: 'StartUp Inc', industry: 'SaaS', conn_count: 1, riskLevel: 'Conservative' }
    ];

    // Framer motion variants for grid staggering
    const containerVariants = {
        hidden: { opacity: 0 },
        show: {
            opacity: 1,
            transition: {
                staggerChildren: 0.1
            }
        }
    };

    const itemVariants = {
        hidden: { opacity: 0, y: 20 },
        show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
    };

    return (
        <div className="p-8 lg:p-12 min-h-screen bg-slate-50 text-slate-800">
            <motion.header
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="flex justify-between items-center mb-10 pb-6 border-b border-slate-200"
            >
                <div>
                    <h1 className="text-4xl font-extrabold text-slate-900 mb-2">My Companies</h1>
                    <p className="text-slate-500">Manage connections and view active AI orchestration environments.</p>
                </div>
                <div>
                    <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        className="bg-indigo-600 hover:bg-indigo-700 transition flex items-center gap-2 text-white font-medium px-5 py-3 rounded-lg shadow-sm"
                    >
                        <Plus size={20} /> Create New Company
                    </motion.button>
                </div>
            </motion.header>

            <motion.div
                className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8"
                variants={containerVariants}
                initial="hidden"
                animate="show"
            >
                {mockCompanies.map((c) => (
                    <motion.div
                        key={c.id}
                        variants={itemVariants}
                        whileHover={{ scale: 1.02 }}
                        className="bg-white border border-slate-200 shadow-sm rounded-2xl p-6 hover:shadow-xl transition-shadow group relative overflow-hidden flex flex-col h-full"
                    >
                        {/* Decoration */}
                        <div className="h-1.5 absolute top-0 left-0 right-0 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>

                        <div className="flex justify-between items-start mb-6 pt-2">
                            <div>
                                <div className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1.5">{c.industry}</div>
                                <h3 className="text-2xl font-extrabold text-slate-900 tracking-tight">{c.name}</h3>
                            </div>
                            <div className="bg-gradient-to-br from-indigo-50 to-purple-50 p-2.5 rounded-xl text-indigo-600 border border-indigo-100/50 shadow-inner" title="Connected Platforms">
                                <Building2 size={24} strokeWidth={1.5} />
                            </div>
                        </div>

                        <div className="flex justify-between items-center border-t border-slate-100 pt-5 mt-2 mb-6">
                            <div className="text-sm border border-slate-200 px-3 py-1 rounded-full text-slate-600 font-medium">
                                {c.conn_count} Connections
                            </div>
                            <div className="text-sm border border-emerald-200 bg-emerald-50 px-3 py-1 rounded-full text-emerald-700 font-bold flex items-center gap-1">
                                <ShieldCheck size={14} /> Risk: {c.riskLevel}
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-3 mt-auto">
                            <button
                                onClick={() => router.push(`/companies/${c.id}/assets/meta`)}
                                className="bg-indigo-50 text-indigo-700 hover:bg-indigo-100 hover:text-indigo-800 transition py-2 rounded-lg font-semibold flex items-center justify-center gap-1 text-sm border border-indigo-100"
                            >
                                View Ads
                            </button>
                            <button
                                onClick={() => router.push(`/companies/${c.id}/assets/tiktok`)}
                                className="bg-emerald-50 text-emerald-700 hover:bg-emerald-100 hover:text-emerald-800 transition py-2 rounded-lg font-semibold flex items-center justify-center gap-1 text-sm border border-emerald-100"
                            >
                                View Social
                            </button>
                            <button
                                onClick={() => router.push(`/companies/${c.id}`)}
                                className="col-span-2 bg-slate-50 text-slate-700 hover:bg-slate-100 hover:text-slate-900 transition py-2 rounded-lg font-semibold flex items-center justify-center gap-1 text-sm border border-slate-200"
                            >
                                All Settings <ArrowRight size={16} />
                            </button>
                        </div>
                    </motion.div>
                ))}

                {/* Empty State / Add Card */}
                <motion.div
                    variants={itemVariants}
                    whileHover={{ scale: 1.02, backgroundColor: "#f8fafc" }}
                    whileTap={{ scale: 0.98 }}
                    className="border-2 border-dashed border-slate-300 rounded-2xl flex flex-col items-center justify-center p-8 text-center bg-slate-50/50 cursor-pointer min-h-[300px] group"
                >
                    <div className="bg-white p-4 rounded-full text-indigo-500 mb-4 shadow-sm border border-slate-100 group-hover:bg-indigo-50 transition-colors">
                        <Plus size={32} />
                    </div>
                    <h3 className="text-xl font-bold text-slate-700 mb-2">Deploy Workspace</h3>
                    <p className="text-slate-500 text-sm max-w-[200px]">Spin up a dedicated AI container for a specific brand.</p>
                </motion.div>
            </motion.div>
        </div>
    );
}
