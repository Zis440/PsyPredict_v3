import React, { createContext, useContext, useState, useCallback, useEffect } from 'react';

export type UserSegment = 'student' | 'professional' | null;

interface SegmentContextType {
  segment: UserSegment;
  setSegment: (s: UserSegment) => void;
  isSegmentSelected: boolean;
  segmentLabel: string;
}

const SegmentContext = createContext<SegmentContextType | null>(null);

const SEGMENT_STORAGE_KEY = 'psypredict_user_segment';

export const SegmentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [segment, setSegmentState] = useState<UserSegment>(() => {
    const saved = localStorage.getItem(SEGMENT_STORAGE_KEY);
    return (saved === 'student' || saved === 'professional') ? saved : null;
  });

  const setSegment = useCallback((s: UserSegment) => {
    setSegmentState(s);
    if (s) {
      localStorage.setItem(SEGMENT_STORAGE_KEY, s);
    } else {
      localStorage.removeItem(SEGMENT_STORAGE_KEY);
    }
  }, []);

  const isSegmentSelected = segment !== null;
  const segmentLabel = segment === 'student' ? 'Student Edition' : segment === 'professional' ? 'Professional Edition' : '';

  return (
    <SegmentContext.Provider value={{ segment, setSegment, isSegmentSelected, segmentLabel }}>
      {children}
    </SegmentContext.Provider>
  );
};

export const useSegment = (): SegmentContextType => {
  const context = useContext(SegmentContext);
  if (!context) throw new Error('useSegment must be used within a SegmentProvider');
  return context;
};
