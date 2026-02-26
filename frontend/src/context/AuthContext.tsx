
import React, { createContext, useEffect, useState } from 'react';
import type { Session, User } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';

interface AuthContextType {
  session: Session | null;
  user: User | null;
  loading: boolean;
  isLocalMode: boolean;
  supabaseError: string | null;
  signInWithEmail: (email: string) => Promise<any>;
  signOut: () => Promise<void>;
  enterLocalMode: () => void;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isLocalMode, setIsLocalMode] = useState(() => {
    return localStorage.getItem('psypredict_local_mode') === 'true';
  });
  const [supabaseError, setSupabaseError] = useState<string | null>(null);

  useEffect(() => {
    // Check if we are in local mode first
    if (isLocalMode) {
      setUser({ id: 'local-guest', email: 'guest@psypredict.local', user_metadata: { full_name: 'Local Guest' } } as any);
      setLoading(false);
      return;
    }

    // Try Supabase Auth
    const authTimeout = setTimeout(() => {
      if (loading) {
        setSupabaseError("Supabase connection timed out. The cloud project might be paused.");
      }
    }, 10000); // 10s timeout

    try {
      supabase.auth.getSession().then(({ data: { session } }) => {
        clearTimeout(authTimeout);
        if (session) {
          setSession(session);
          setUser(session.user);
        }
        setLoading(false);
      }).catch(err => {
        clearTimeout(authTimeout);
        console.warn("Supabase session check failed (expected if offline/paused):", err);
        setSupabaseError("Could not connect to Supabase Cloud.");
        setLoading(false);
      });

      const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
        setSession(session);
        setUser(session?.user ?? null);
        setLoading(false);
      });

      return () => {
        clearTimeout(authTimeout);
        subscription.unsubscribe();
      };
    } catch (err) {
      clearTimeout(authTimeout);
      console.error("Auth init error:", err);
      setSupabaseError("Auth initialization failed.");
      setLoading(false);
    }
  }, [isLocalMode]);

  const enterLocalMode = () => {
    setIsLocalMode(true);
    localStorage.setItem('psypredict_local_mode', 'true');
    setUser({ id: 'local-guest', email: 'guest@psypredict.local', user_metadata: { full_name: 'Local Guest' } } as any);
  };

  const signInWithEmail = async (_email: string) => { return; };

  const signOut = async () => {
    if (isLocalMode) {
      setIsLocalMode(false);
      localStorage.removeItem('psypredict_local_mode');
      setUser(null);
    } else {
      await supabase.auth.signOut();
    }
  };

  const value = {
    session,
    user,
    loading,
    isLocalMode,
    supabaseError,
    signInWithEmail,
    signOut,
    enterLocalMode,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
