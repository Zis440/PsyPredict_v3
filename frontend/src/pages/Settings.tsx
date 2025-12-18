import React, { useState, useEffect } from 'react';
import Navbar from '../components/common/Navbar';
import { useAuth } from '../hooks/useAuth';
import { supabase } from '../lib/supabase';
import { motion } from 'framer-motion';
import { Save, AlertCircle, CheckCircle } from 'lucide-react';

const Settings: React.FC = () => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
  });
  
  const [isEditingPassword, setIsEditingPassword] = useState(false);

  // Check if user signed in via Email/Password provider
  const isEmailProvider = user?.app_metadata?.provider === 'email';

  useEffect(() => {
    if (user) {
      setFormData(prev => ({
        ...prev,
        fullName: user.user_metadata?.full_name || '',
        email: user.email || '',
      }));
    }
  }, [user]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);

    try {
      const updates: any = {
        data: { full_name: formData.fullName },
      };

      if (formData.email !== user?.email) {
        updates.email = formData.email;
      }

      if (formData.password) {
        updates.password = formData.password;
      }

      const { error } = await supabase.auth.updateUser(updates);

      if (error) throw error;

      setMessage({
        type: 'success',
        text: 'Profile updated successfully!',
      });
      
      if (formData.email !== user?.email) {
         setMessage({
            type: 'success',
            text: 'Profile updated! Please check your new email for a confirmation link.',
         });
      }
      
      
      // Clear password field and exit edit mode after successful update
      setFormData(prev => ({ ...prev, password: '' }));
      setIsEditingPassword(false);
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.message || 'Error updating profile',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      
      <main className="flex-1 max-w-4xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-12">
        <motion.div
           initial={{ opacity: 0, y: 20 }}
           animate={{ opacity: 1, y: 0 }}
           className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden"
        >
          <div className="px-6 py-8 sm:p-10">
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-gray-900">Account Settings</h1>
              <p className="text-gray-500 mt-2">Manage your profile information and security settings.</p>
            </div>

            {message && (
              <div className={`mb-6 p-4 rounded-xl flex items-start gap-3 ${
                message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
              }`}>
                {message.type === 'success' ? <CheckCircle size={20} className="shrink-0 mt-0.5" /> : <AlertCircle size={20} className="shrink-0 mt-0.5" />}
                <p className="text-sm font-medium">{message.text}</p>
              </div>
            )}

            <form onSubmit={handleUpdateProfile} className="space-y-6">
              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Full Name
                </label>
                <input
                  type="text"
                  name="fullName"
                  value={formData.fullName}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                  placeholder="Your Name"
                />
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  name="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                  placeholder="you@example.com"
                />
                <p className="mt-2 text-xs text-gray-500">
                  Note: Changing your email will require re-verification.
                </p>
              </div>

              {/* Password - Only for Email Providers */}
              {isEmailProvider && (
                <div className="pt-6 border-t border-gray-100">
                  <div className="flex justify-between items-center mb-2">
                    <label className="block text-sm font-medium text-gray-700">
                      Password
                    </label>
                    <button
                      type="button"
                      onClick={() => {
                        setIsEditingPassword(!isEditingPassword);
                        setFormData(prev => ({ ...prev, password: '' })); // Clear on toggle
                      }}
                      className="text-sm text-indigo-600 hover:text-indigo-800 font-medium"
                    >
                      {isEditingPassword ? 'Cancel' : 'Change Password'}
                    </button>
                  </div>

                  {!isEditingPassword ? (
                    <div className="w-full px-4 py-3 border border-gray-200 bg-gray-50 rounded-xl text-gray-500 font-mono text-sm">
                      ••••••••••••
                    </div>
                  ) : (
                    <div className="space-y-2">
                       <input
                        type="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                        placeholder="Enter new password"
                        minLength={6}
                      />
                      <p className="text-xs text-gray-500">
                        Must be at least 6 characters long.
                      </p>
                    </div>
                  )}
                </div>
              )}

              <div className="pt-6 flex justify-end">
                <button
                  type="submit"
                  disabled={loading}
                  className="flex items-center gap-2 bg-indigo-600 text-white px-6 py-3 rounded-xl font-semibold hover:bg-indigo-700 disabled:opacity-50 transition-colors shadow-sm cursor-pointer"
                >
                  {loading ? (
                    'Saving...'
                  ) : (
                    <>
                      <Save size={18} />
                      Save Changes
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </motion.div>
      </main>
    </div>
  );
};

export default Settings;
