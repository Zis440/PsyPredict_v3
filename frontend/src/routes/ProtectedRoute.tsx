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
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export const Login: React.FC = () => {
  const { user, enterLocalMode, authError } = useAuth();
  const { signIn } = useAuthActions();
  const [error, setError] = React.useState<string | null>(null);
  const [loading, setLoading] = React.useState(false);

  React.useEffect(() => {
    if (user) window.location.href = '/dashboard';
  }, [user]);

  const handleOAuthLogin = async (provider: 'google' | 'microsoft-entra-id') => {
    setLoading(true);
    setError(null);
    try {
      await signIn(provider, { redirectTo: '/dashboard' });
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please try again.');
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
            <h2 className="text-2xl font-bold text-gray-900">Welcome to PsyPredict</h2>
            <p className="text-gray-500 mt-2 text-sm">
              Sign in to access your dashboard
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
                    <span className="font-bold leading-tight">Connection Issue Detected</span>
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

            {/* Google */}
            <button
              onClick={() => handleOAuthLogin('google')}
              disabled={loading}
              className="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              <svg className="h-5 w-5" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4" />
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853" />
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05" />
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335" />
              </svg>
              <span className="text-sm font-medium text-gray-700">Continue with Google</span>
            </button>

            {/* Microsoft */}
            <button
              onClick={() => handleOAuthLogin('microsoft-entra-id')}
              disabled={loading}
              className="w-full flex items-center justify-center gap-3 px-4 py-3 border border-gray-300 rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50"
            >
              <svg className="h-5 w-5" viewBox="0 0 21 21">
                <rect x="1" y="1" width="9" height="9" fill="#F25022" />
                <rect x="1" y="11" width="9" height="9" fill="#00A4EF" />
                <rect x="11" y="1" width="9" height="9" fill="#7FBA00" />
                <rect x="11" y="11" width="9" height="9" fill="#FFB900" />
              </svg>
              <span className="text-sm font-medium text-gray-700">Continue with Microsoft</span>
            </button>
          </div>

          <div className="mt-8 flex flex-col items-center gap-3">
            <div className="w-16 border-t border-gray-200"></div>
            <button
              onClick={() => enterLocalMode()}
              className="text-xs text-gray-400 hover:text-indigo-600 transition-colors uppercase tracking-widest font-bold"
            >
              Run In Offline Mode
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};
