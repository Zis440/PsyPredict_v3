import React from 'react';
import { Navigate, useLocation, useNavigate } from 'react-router-dom';
import { useAuth, SignIn, SignUp } from '@clerk/react';
import { useGuestMode } from '../context/GuestModeContext';

export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isLoaded, isSignedIn } = useAuth();
  const { isGuestMode } = useGuestMode();
  const location = useLocation();

  // Guest mode bypasses Clerk middleware entirely
  if (isGuestMode) {
    return <>{children}</>;
  }

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="relative">
          <div className="text-6xl">🧠</div>
          <div className="absolute bottom-0 right-0 w-4 h-4 border-2 border-gray-300 border-t-gray-900 rounded-full animate-spin"></div>
        </div>
      </div>
    );
  }

  if (!isSignedIn) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export const Login: React.FC = () => {
  const { isSignedIn, isLoaded } = useAuth();
  const { exitGuestMode, enterGuestMode } = useGuestMode();
  const navigate = useNavigate();
  const [mode, _setMode] = React.useState<'signIn' | 'signUp'>('signIn');

  // Clear guest state when user arrives at the auth page
  React.useEffect(() => {
    exitGuestMode();
  }, []);

  if (isLoaded && isSignedIn) {
    return <Navigate to="/dashboard" replace />;
  }

  const handleGuestMode = () => {
    enterGuestMode();
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4 py-12">
      <div className="mb-8 text-center">
        <span className="text-4xl block mb-2">🧠</span>
        <h2 className="text-2xl font-bold text-gray-900">PsyPredict</h2>
        <p className="text-sm text-gray-500 mt-1">Clinical Psychological Analysis</p>
      </div>

      <div className="w-full max-w-[400px]">
        {mode === 'signIn' ? (
          <div className="flex flex-col items-center">
            <SignIn routing="hash" fallbackRedirectUrl="/dashboard" />
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <SignUp routing="hash" fallbackRedirectUrl="/dashboard" />
          </div>
        )}

        {/* Divider */}
        <div className="flex items-center gap-3 mt-6">
          <div className="flex-1 h-px bg-gray-200" />
          <span className="text-xs text-gray-400 font-medium">or</span>
          <div className="flex-1 h-px bg-gray-200" />
        </div>

        {/* Guest Mode CTA */}
        <button
          onClick={handleGuestMode}
          className="mt-4 w-full flex items-center justify-center gap-2 border border-dashed border-gray-300 text-gray-500 px-4 py-2.5 rounded-xl text-sm font-medium hover:border-gray-400 hover:text-gray-700 hover:bg-gray-50 transition-all"
        >
          <span className="text-base">👤</span>
          Continue as Guest
        </button>
        <p className="mt-2 text-center text-[11px] text-gray-400">
          No account needed — your session data won't be saved
        </p>
      </div>
    </div>
  );
};
