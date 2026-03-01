import { useState } from 'react';
import { Check, X, ShieldAlert } from 'lucide-react';
import '../App.css';

const MOCK_EXECUTIONS = [
    {
        id: "rec_fb9281ja",
        platform: "Meta Ads",
        action: "BUDGET_INCREASE",
        detail: "Scale campaign 'Lookalike Audiences' from $1000 to $1250 daily.",
        risk_assessment: "LOW",
        status: "pending"
    },
    {
        id: "rec_91823kzm",
        platform: "Google Ads",
        action: "PAUSE_CREATIVE",
        detail: "Pause 'Summer Sale Video 1' due to Fatigue Threshold break.",
        risk_assessment: "LOW",
        status: "pending"
    },
    {
        id: "rec_zb192msd",
        platform: "Shopify/Meta",
        action: "CREATE_VARIANT",
        detail: "Launch new Retargeting creative focusing on Urgency/Scarcity angle.",
        risk_assessment: "MEDIUM",
        status: "pending"
    }
];

const ExecutionPipeline = () => {
    const [executions, setExecutions] = useState(MOCK_EXECUTIONS);

    const handleAction = (id: string, action_type: "approve" | "reject") => {
        setExecutions(prev =>
            prev.map(item =>
                item.id === id ? { ...item, status: action_type === 'approve' ? 'approved' : 'rejected' } : item
            )
        );
    };

    const handleKillSwitch = () => {
        if (window.confirm("CRITICAL WARNING: This will immediately pause ALL campaigns globally across platforms. Proceed?")) {
            alert("KILL SWITCH ACTIVATED. Campaigns paused.");
        }
    };

    return (
        <div className="page-content">
            <div className="header border-danger-glass">
                <div>
                    <h1 className="page-title">Execution Pipeline</h1>
                    <p className="page-subtitle text-danger">Autonomous Operations / Manual Hooks</p>
                </div>
                <button className="btn kill-switch-btn" onClick={handleKillSwitch}>
                    <ShieldAlert size={18} /> EMERGENCY KILL SWITCH
                </button>
            </div>

            <div className="execution-list mt-8">
                <h3 className="section-subtitle mb-4">Pending Approvals</h3>
                {executions.map((exec) => (
                    <div key={exec.id} className={`exec-card ${exec.status !== 'pending' ? 'completed glass-dim' : 'glass-card'}`}>
                        <div className="exec-header">
                            <span className="badge">{exec.platform}</span>
                            <span className={`badge ${exec.risk_assessment === 'LOW' ? 'success' : 'warning'}`}>
                                Risk: {exec.risk_assessment}
                            </span>
                        </div>

                        <div className="exec-body mt-4 mb-4">
                            <strong>{exec.action.replace('_', ' ')}</strong>
                            <p className="text-muted mt-2">{exec.detail}</p>
                        </div>

                        {exec.status === 'pending' ? (
                            <div className="exec-actions mt-4 action-footer border-t-glass pt-4">
                                <button
                                    className="btn btn-primary btn-sm flex-center gap-2"
                                    onClick={() => handleAction(exec.id, 'approve')}
                                >
                                    <Check size={16} /> Approve
                                </button>
                                <button
                                    className="btn btn-danger btn-sm flex-center gap-2"
                                    onClick={() => handleAction(exec.id, 'reject')}
                                >
                                    <X size={16} /> Reject
                                </button>
                            </div>
                        ) : (
                            <div className="exec-actions mt-4 action-footer border-t-glass pt-4">
                                <span className={`status-text ${exec.status === 'approved' ? 'text-success' : 'text-danger'}`}>
                                    {exec.status.toUpperCase()}
                                </span>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ExecutionPipeline;
