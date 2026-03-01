import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Link from 'next/link';
import { LayoutDashboard, Users, Workflow, Calendar, Settings } from 'lucide-react';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'AI Marketing Intelligence SaaS',
  description: 'Multi-platform autonomous intelligence',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-slate-50 flex min-h-screen text-slate-800`}>
        {/* Navigation Sidebar */}
        <nav className="w-64 bg-slate-900 text-slate-300 flex flex-col p-6 h-screen sticky top-0 border-r border-slate-800">
          <div className="text-xl font-bold text-white mb-10 flex items-center gap-3">
            <span className="bg-indigo-600 p-2 rounded-lg text-white shadow-lg">AI</span>
            Intelligence
          </div>

          <ul className="space-y-4 font-medium flex-1">
            <li>
              <Link href="/dashboard" className="flex items-center gap-3 hover:text-white hover:bg-slate-800 p-3 rounded-lg transition">
                <LayoutDashboard size={20} /> Dashboard
              </Link>
            </li>
            <li>
              <Link href="/companies" className="flex items-center gap-3 hover:text-white hover:bg-slate-800 p-3 rounded-lg transition">
                <Users size={20} /> My Companies
              </Link>
            </li>
            <li>
              <Link href="/companies/default/calendar" className="flex items-center gap-3 hover:text-white hover:bg-slate-800 p-3 rounded-lg transition">
                <Calendar size={20} /> Content Calendar
              </Link>
            </li>
            <li>
              <Link href="/companies/default/automation" className="flex items-center gap-3 hover:text-white hover:bg-slate-800 p-3 rounded-lg transition text-indigo-400">
                <Workflow size={20} /> AI Safety Engine
              </Link>
            </li>
          </ul>

          <div className="pt-6 border-t border-slate-800">
            <Link href="/profile" className="flex items-center gap-3 hover:text-white hover:bg-slate-800 p-3 rounded-lg transition">
              <Settings size={20} /> Profile & Settings
            </Link>
          </div>
        </nav>

        {/* Main Content Area */}
        <main className="flex-1 w-full overflow-hidden">
          {children}
        </main>
      </body>
    </html>
  );
}
