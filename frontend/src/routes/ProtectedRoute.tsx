import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth, SignIn, SignUp } from '@clerk/react';

export const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isLoaded, isSignedIn } = useAuth();
  const location = useLocation();

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
  const [mode, setMode] = React.useState<'signIn' | 'signUp'>('signIn');

  if (isLoaded && isSignedIn) {
    return <Navigate to="/dashboard" replace />;
  }

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
            <SignIn routing="hash" />
            <button 
              onClick={() => setMode('signUp')}
              className="mt-6 text-sm text-gray-500 hover:text-indigo-600 font-medium transition-colors"
            >
              Don't have an account? Sign up
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center">
            <SignUp routing="hash" />
            <button 
              onClick={() => setMode('signIn')}
              className="mt-6 text-sm text-gray-500 hover:text-indigo-600 font-medium transition-colors"
            >
              Already have an account? Sign in
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
