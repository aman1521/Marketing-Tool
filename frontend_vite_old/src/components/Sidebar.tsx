import { NavLink } from 'react-router-dom';
import { Activity, BrainCircuit, LayoutDashboard, Settings, Layers, LineChart, Building2, CreditCard } from 'lucide-react';
import '../App.css';

const Sidebar = () => {
    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="logo-icon"><BrainCircuit color="#fff" size={24} /></div>
                <span className="logo-text">AI Growth OS</span>
            </div>

            <nav className="sidebar-nav">
                <NavLink to="/" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
                    <LayoutDashboard size={20} />
                    <span>Analytics & Intents</span>
                </NavLink>

                <NavLink to="/strategy" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
                    <Activity size={20} />
                    <span>Strategy Orchestrator</span>
                </NavLink>

                <NavLink to="/execution" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
                    <Layers size={20} />
                    <span>Execution Pipeline</span>
                </NavLink>

                <NavLink to="/analytics" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
                    <LineChart size={20} />
                    <span>Analytics & Reporting</span>
                </NavLink>

                <NavLink to="/companies" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
                    <Building2 size={20} />
                    <span>Company Profiles</span>
                </NavLink>
            </nav>

            <div className="sidebar-footer">
                <NavLink to="/billing" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
                    <CreditCard size={20} />
                    <span>Billing & Upgrades</span>
                </NavLink>
                <NavLink to="/settings" className={({ isActive }) => isActive ? "nav-item active" : "nav-item"}>
                    <Settings size={20} />
                    <span>Settings</span>
                </NavLink>
                <div className="user-profile">
                    <div className="avatar">A</div>
                    <div className="user-info">
                        <span className="user-name">Admin</span>
                        <span className="user-role">Operating System</span>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
