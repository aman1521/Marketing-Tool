import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import DashboardInsights from './components/DashboardInsights';
import StrategyEngine from './components/StrategyEngine';
import ExecutionPipeline from './components/ExecutionPipeline';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import Settings from './components/Settings';
import Auth from './components/Auth';
import Companies from './components/Companies';
import Billing from './components/Billing';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<DashboardInsights />} />
            <Route path="/strategy" element={<StrategyEngine />} />
            <Route path="/execution" element={<ExecutionPipeline />} />
            <Route path="/analytics" element={<AnalyticsDashboard />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/auth" element={<Auth />} />
            <Route path="/companies" element={<Companies />} />
            <Route path="/billing" element={<Billing />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
