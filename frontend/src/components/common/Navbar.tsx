import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { UserButton, useUser } from '@clerk/react';
import { Menu, X, Settings, LayoutDashboard, History, LogIn, BarChart3 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGuestMode } from '../../context/GuestModeContext';

const Navbar: React.FC = () => {
  const { user } = useUser();
  const { isGuestMode, exitGuestMode } = useGuestMode();
  const location = useLocation();
  const navigate = useNavigate();
  const [isOpen, setIsOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  const navLinks = [
    { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    // { path: '/assessments', label: 'Assessments', icon: LayoutDashboard }, // Added Assessments link
    { path: '/progress',  label: 'Progress',  icon: BarChart3 },
    { path: '/history',   label: 'History',   icon: History },
    { path: '/settings',  label: 'Settings',  icon: Settings },
  ];

  const handleSignIn = () => {
    exitGuestMode();
    navigate('/auth');
  };

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">

          {/* Logo */}
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center gap-2">
              <span className="text-2xl">🧠</span>
              <span className="font-bold text-xl text-gray-900 tracking-tight">PsyPredict</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-6">
            <div className="flex items-center gap-1 bg-gray-100/50 p-1 rounded-full">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`
                    flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all
                    ${isActive(link.path)
                      ? 'bg-white text-indigo-600 shadow-sm'
                      : 'text-gray-500 hover:text-gray-900 hover:bg-gray-200/50'}
                  `}
                >
                  <link.icon size={16} />
                  {link.label}
                </Link>
              ))}
            </div>

            <div className="h-6 w-px bg-gray-200" />

            {/* Guest Mode: badge + sign-in button */}
            {isGuestMode ? (
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 px-3 py-1.5 rounded-full">
                  <span className="text-sm">👤</span>
                  <span className="text-xs font-semibold text-amber-700">Guest Mode</span>
                  <span className="hidden lg:inline text-[10px] text-amber-500 font-medium">• Data is temporary</span>
                </div>
                <motion.button
                  whileHover={{ scale: 1.04 }}
                  whileTap={{ scale: 0.96 }}
                  onClick={handleSignIn}
                  className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-full text-sm font-semibold hover:bg-indigo-700 transition-colors"
                >
                  <LogIn size={15} />
                  Sign In
                </motion.button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <div className="hidden lg:block text-right mr-2">
                  <p className="text-sm font-medium text-gray-900 leading-none">
                    {user?.fullName || 'User'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {user?.primaryEmailAddress?.emailAddress}
                  </p>
                </div>
                <UserButton appearance={{ elements: { userButtonAvatarBox: 'w-8 h-8' } }} />
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="flex items-center md:hidden gap-4">
            {isGuestMode ? (
              <button
                onClick={handleSignIn}
                className="flex items-center gap-1.5 bg-indigo-600 text-white px-3 py-1.5 rounded-full text-xs font-semibold"
              >
                <LogIn size={13} /> Sign In
              </button>
            ) : (
              <UserButton appearance={{ elements: { userButtonAvatarBox: 'w-8 h-8' } }} />
            )}
            <button
              onClick={() => setIsOpen(!isOpen)}
              className="p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none"
            >
              {isOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Navigation */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-gray-200 bg-white overflow-hidden"
          >
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              {isGuestMode && (
                <div className="flex items-center gap-2 px-3 py-2 mb-2 bg-amber-50 rounded-md border border-amber-200">
                  <span className="text-sm">👤</span>
                  <span className="text-xs font-semibold text-amber-700">Guest Mode — data is temporary</span>
                </div>
              )}
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  onClick={() => setIsOpen(false)}
                  className={`
                    flex items-center gap-3 px-3 py-3 rounded-md text-base font-medium
                    ${isActive(link.path)
                      ? 'bg-indigo-50 text-indigo-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}
                  `}
                >
                  <link.icon size={20} />
                  {link.label}
                </Link>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};

export default Navbar;
