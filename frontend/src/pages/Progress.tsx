import React from 'react';
import Navbar from '../components/common/Navbar';
import ProgressDashboard from '../components/features/ProgressDashboard';
import { useUser } from '@clerk/react';
import { useGuestMode } from '../context/GuestModeContext';
import { motion } from 'framer-motion';
import { BarChart3, Lock } from 'lucide-react';

const Progress: React.FC = () => {
  const { user } = useUser();
  const { isGuestMode } = useGuestMode();
  const userId = user?.id || '';

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
                <BarChart3 className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Your Progress</h1>
                <p className="text-sm text-gray-500">Track your emotional wellness journey over time</p>
              </div>
            </div>
          </div>

          {/* Content */}
          {isGuestMode ? (
            <div className="bg-white rounded-2xl border border-gray-200 p-12 text-center shadow-sm">
              <Lock className="w-12 h-12 mx-auto mb-4 text-gray-300" />
              <h2 className="text-lg font-semibold text-gray-700 mb-2">Sign in to track progress</h2>
              <p className="text-sm text-gray-500 max-w-md mx-auto">
                Create an account to unlock your personal progress dashboard with emotion trends,
                risk trajectory analysis, and AI-powered clinical insights.
              </p>
            </div>
          ) : (
            <ProgressDashboard userId={userId} />
          )}
        </motion.div>
      </main>
    </div>
  );
};

export default Progress;
