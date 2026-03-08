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
  authError: string | null;
  signOut: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isLoading: convexLoading } = useConvexAuth();
  const { signOut: convexSignOut } = useAuthActions();

  const [user, setUser] = useState<UserInfo | null>(null);
  const [authError, setAuthError] = useState<string | null>(null);

  // Fetch the user profile from Convex when authenticated
  const profile = useQuery(
    api.users.currentUser,
    isAuthenticated ? {} : "skip"
  );

  // Handle Convex auth state
  useEffect(() => {
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
  }, [isAuthenticated, profile, convexLoading]);

  const signOut = async () => {
    await convexSignOut();
    setUser(null);
  };

  const value = {
    user,
    loading: convexLoading,
    authError,
    signOut,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
