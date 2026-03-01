import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BrainCircuit, Mail, Lock, User } from 'lucide-react';
import '../App.css';

const Auth = () => {
    const [isLogin, setIsLogin] = useState(true);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        // Simulate API Call
        setTimeout(() => {
            setLoading(false);
            // On success navigate to dashboard
            navigate("/");
        }, 1200);
    };

    return (
        <div className="auth-container fade-in">
            <div className="auth-card glass-panel">
                <div className="auth-header">
                    <div className="logo-icon blur-glow" style={{ marginBottom: '1rem', background: 'linear-gradient(135deg, #10b981, #0ea5e9)', padding: '12px', borderRadius: '12px' }}>
                        <BrainCircuit color="#fff" size={32} />
                    </div>
                    <h2>{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
                    <p className="text-muted">
                        {isLogin ? 'Enter your credentials to access your autonomous AI.' : 'Start your multi-tenant SaaS journey today.'}
                    </p>
                </div>

                <form className="auth-form" onSubmit={handleSubmit}>
                    {!isLogin && (
                        <div className="form-group">
                            <label>Full Name</label>
                            <div className="input-with-icon">
                                <User size={18} className="input-icon" />
                                <input type="text" className="glass-input" placeholder="John Doe" required />
                            </div>
                        </div>
                    )}

                    <div className="form-group">
                        <label>Email Address</label>
                        <div className="input-with-icon">
                            <Mail size={18} className="input-icon" />
                            <input type="email" className="glass-input" placeholder="admin@enterprise.com" required />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <div className="input-with-icon">
                            <Lock size={18} className="input-icon" />
                            <input type="password" className="glass-input" placeholder="••••••••" required />
                        </div>
                    </div>

                    <button type="submit" className="button bg-primary w-100 mt-4" disabled={loading} style={{ width: '100%', justifyContent: 'center', padding: '0.75rem' }}>
                        {loading ? 'Authenticating...' : (isLogin ? 'Sign In' : 'Create Account')}
                    </button>
                </form>

                <div className="auth-footer">
                    <p className="text-muted">
                        {isLogin ? "Don't have an account? " : "Already have an account? "}
                        <span className="text-primary auth-toggle" onClick={() => setIsLogin(!isLogin)} style={{ cursor: 'pointer', fontWeight: 600 }}>
                            {isLogin ? 'Sign Up' : 'Log In'}
                        </span>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default Auth;
