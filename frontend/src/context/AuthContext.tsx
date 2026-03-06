import React, { createContext, useEffect, useState } from 'react';
import { useConvexAuth } from "convex/react";
import { useAuthActions } from "@convex-dev/auth/react";
import { useQuery } from "convex/react";
import { api } from "../../convex/_generated/api";

interface UserInfo {
  id: string;
  email: string | null;
  fullName: string | null;
  avatarUrl: string | null;
}

interface AuthContextType {
  user: UserInfo | null;
  loading: boolean;
  isLocalMode: boolean;
  authError: string | null;
  signOut: () => Promise<void>;
  enterLocalMode: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading: convexLoading } = useConvexAuth();
  const { signOut: convexSignOut } = useAuthActions();

  const [user, setUser] = useState<UserInfo | null>(null);
  const [isLocalMode, setIsLocalMode] = useState(() => {
    return localStorage.getItem('psypredict_local_mode') === 'true';
  });
  const [authError, setAuthError] = useState<string | null>(null);

  // Fetch the user profile from Convex when authenticated
  const profile = useQuery(
    api.users.currentUser,
    isAuthenticated && !isLocalMode ? {} : "skip"
  );

  // Handle local mode
  useEffect(() => {
    if (isLocalMode) {
      setUser({
        id: 'local-guest',
        email: 'guest@psypredict.local',
        fullName: 'Local Guest',
        avatarUrl: null,
      });
      setAuthError(null);
    }
  }, [isLocalMode]);

  // Handle Convex auth state
  useEffect(() => {
    if (isLocalMode) return;

    if (isAuthenticated && profile) {
      setUser({
        id: profile.userId,
        email: profile.email ?? null,
        fullName: profile.fullName ?? null,
        avatarUrl: profile.avatarUrl ?? null,
      });
      setAuthError(null);
    } else if (!isAuthenticated && !convexLoading) {
      setUser(null);
    }
  }, [isAuthenticated, profile, convexLoading, isLocalMode]);

  const enterLocalMode = () => {
    setIsLocalMode(true);
    localStorage.setItem('psypredict_local_mode', 'true');
    setUser({
      id: 'local-guest',
      email: 'guest@psypredict.local',
      fullName: 'Local Guest',
      avatarUrl: null,
    });
  };

  const signOut = async () => {
    if (isLocalMode) {
      setIsLocalMode(false);
      localStorage.removeItem('psypredict_local_mode');
      setUser(null);
    } else {
      await convexSignOut();
      setUser(null);
    }
  };

  const loading = isLocalMode ? false : convexLoading;

  const value = {
    user,
    loading,
    isLocalMode,
    authError,
    signOut,
    enterLocalMode,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
