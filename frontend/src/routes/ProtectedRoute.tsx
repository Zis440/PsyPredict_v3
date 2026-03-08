import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { useAuthActions } from "@convex-dev/auth/react";
import { motion } from 'framer-motion';
import { AlertTriangle } from 'lucide-react';

export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="relative">
          <div className="text-6xl">🧠</div>
          <div className="absolute bottom-0 right-0 w-4 h-4 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export const Login: React.FC = () => {
  const { user, enterLocalMode, authError } = useAuth();
  const { signIn } = useAuthActions();
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [step, setStep] = React.useState<'signIn' | 'signUp'>('signIn');

  // Form fields
  const [email, setEmail] = React.useState('');
  const [password, setPassword] = React.useState('');
  const [name, setName] = React.useState('');

  React.useEffect(() => {
    if (user) window.location.href = '/dashboard';
  }, [user]);

  const validateForm = (): string | null => {
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return 'Please enter a valid email address.';
    }
    if (password.length < 8) return 'Password must be at least 8 characters.';
    if (!/[a-z]/.test(password)) return 'Password must contain a lowercase letter.';
    if (!/[A-Z]/.test(password)) return 'Password must contain an uppercase letter.';
    if (!/\d/.test(password)) return 'Password must contain a number.';
    return null;
  };

  const handlePasswordAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.set('email', email);
      formData.set('password', password);
      formData.set('flow', step);
      if (step === 'signUp' && name) {
        formData.set('name', name);
      }
      await signIn('password', formData);
    } catch (err: any) {
      const msg = err?.data ?? err?.message ?? 'Authentication failed. Please try again.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
      setLoading(false);
    }
  };



  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-md w-full bg-white rounded-3xl shadow-xl overflow-hidden"
      >
        <div className="p-8">
          <div className="text-center mb-8">
            <span className="text-4xl block mb-2">🧠</span>
            <h2 className="text-2xl font-bold text-gray-900">
              {step === 'signIn' ? 'Welcome Back' : 'Create Account'}
            </h2>
            <p className="text-gray-500 mt-2 text-sm">
              {step === 'signIn'
                ? 'Sign in to access your dashboard'
                : 'Sign up to get started with PsyPredict'}
            </p>
          </div>

          <div className="space-y-4">
            {(error || authError) && (
              <div className="bg-amber-50 border border-amber-200 text-amber-800 p-4 rounded-2xl text-sm flex flex-col gap-3 shadow-sm">
                <div className="flex items-start gap-3">
                  <div className="bg-amber-100 p-1.5 rounded-lg shrink-0">
                    <AlertTriangle size={18} className="text-amber-600" />
                  </div>
                  <div className="flex flex-col gap-1">
                    <span className="font-bold leading-tight">
                      {step === 'signUp' ? 'Sign-up Issue' : 'Sign-in Issue'}
                    </span>
                    <span className="text-amber-700/80 text-xs leading-relaxed">
                      {authError || error}
                    </span>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => enterLocalMode()}
                  className="w-full bg-amber-600/10 hover:bg-amber-600/20 text-amber-700 py-2.5 rounded-xl font-bold text-xs transition-colors border border-amber-600/20"
                >
                  Switch to Offline Mode (Guest) →
                </button>
              </div>
            )}

            {/* Email / Password Form */}
            <form onSubmit={handlePasswordAuth} className="space-y-3">
              {step === 'signUp' && (
                <input
                  name="name"
                  type="text"
                  placeholder="Full Name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
                />
              )}
              <input
                name="email"
                type="email"
                placeholder="Email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
              <input
                name="password"
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full px-4 py-3 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all"
              />
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-indigo-600 text-white py-3 rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-colors disabled:opacity-50"
              >
                {loading ? 'Please wait…' : step === 'signIn' ? 'Sign In' : 'Sign Up'}
              </button>
            </form>

            <button
              type="button"
              onClick={() => {
                setStep(step === 'signIn' ? 'signUp' : 'signIn');
                setError(null);
              }}
              className="w-full text-xs text-gray-500 hover:text-indigo-600 transition-colors font-medium"
            >
              {step === 'signIn'
                ? "Don't have an account? Sign up"
                : 'Already have an account? Sign in'}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
