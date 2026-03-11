import React, { createContext, useContext, useState, useCallback } from 'react';

export interface GuestMessage {
  role: 'user' | 'assistant';
  content: string;
  report?: any;
  fusionScore?: number;
  remedy?: any;
}

export interface GuestConversation {
  id: string;
  title: string;
  createdAt: string;
  messages: GuestMessage[];
}

interface GuestModeContextType {
  isGuestMode: boolean;
  enterGuestMode: () => void;
  exitGuestMode: () => void;
  guestConversations: GuestConversation[];
  createGuestConversation: (title: string) => string;
  updateGuestConversation: (id: string, messages: GuestMessage[]) => void;
  getGuestConversation: (id: string) => GuestConversation | undefined;
}

const GuestModeContext = createContext<GuestModeContextType | null>(null);

export const GuestModeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isGuestMode, setIsGuestMode] = useState(false);
  const [guestConversations, setGuestConversations] = useState<GuestConversation[]>([]);

  const enterGuestMode = useCallback(() => setIsGuestMode(true), []);

  const exitGuestMode = useCallback(() => {
    setIsGuestMode(false);
    setGuestConversations([]);
  }, []);

  const createGuestConversation = useCallback((title: string): string => {
    const id = `guest-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const newConv: GuestConversation = {
      id,
      title,
      createdAt: new Date().toISOString(),
      messages: [],
    };
    setGuestConversations(prev => [...prev, newConv]);
    return id;
  }, []);

  const updateGuestConversation = useCallback((id: string, messages: GuestMessage[]) => {
    setGuestConversations(prev =>
      prev.map(conv => conv.id === id ? { ...conv, messages } : conv)
    );
  }, []);

  const getGuestConversation = useCallback(
    (id: string) => guestConversations.find(conv => conv.id === id),
    [guestConversations]
  );

  return (
    <GuestModeContext.Provider value={{
      isGuestMode,
      enterGuestMode,
      exitGuestMode,
      guestConversations,
      createGuestConversation,
      updateGuestConversation,
      getGuestConversation,
    }}>
      {children}
    </GuestModeContext.Provider>
  );
};

export const useGuestMode = (): GuestModeContextType => {
  const context = useContext(GuestModeContext);
  if (!context) throw new Error('useGuestMode must be used within a GuestModeProvider');
  return context;
};
