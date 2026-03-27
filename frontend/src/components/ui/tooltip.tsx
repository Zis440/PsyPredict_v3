/**
 * Tooltip — shadcn/ui-compatible implementation (no Radix dependency).
 * API matches shadcn's Tooltip so it can be swapped in later with zero refactoring.
 *
 * Usage:
 *   <TooltipProvider>
 *     <Tooltip>
 *       <TooltipTrigger asChild>
 *         <button disabled>…</button>
 *       </TooltipTrigger>
 *       <TooltipContent>Log in to use this feature</TooltipContent>
 *     </Tooltip>
 *   </TooltipProvider>
 */

import React, { createContext, useContext, useState } from 'react';

// ── Context ──────────────────────────────────────────────────────────────────
const TooltipCtx = createContext<{
  open: boolean;
  setOpen: (v: boolean) => void;
}>({ open: false, setOpen: () => {} });

// ── TooltipProvider ──────────────────────────────────────────────────────────
export const TooltipProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <>{children}</>
);

// ── Tooltip ──────────────────────────────────────────────────────────────────
export const Tooltip: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [open, setOpen] = useState(false);
  return (
    <TooltipCtx.Provider value={{ open, setOpen }}>
      <div className="relative inline-flex items-center">
        {children}
      </div>
    </TooltipCtx.Provider>
  );
};

// ── TooltipTrigger ───────────────────────────────────────────────────────────
interface TooltipTriggerProps {
  children: React.ReactNode;
  /** Mirror shadcn's asChild — renders the child directly inside a hover-aware wrapper */
  asChild?: boolean;
}

export const TooltipTrigger: React.FC<TooltipTriggerProps> = ({ children, asChild: _asChild }) => {
  const { setOpen } = useContext(TooltipCtx);

  // Always wrap in a div so pointer events fire even on disabled buttons
  return (
    <div
      className="inline-flex items-center"
      onMouseEnter={() => setOpen(true)}
      onMouseLeave={() => setOpen(false)}
      onFocus={() => setOpen(true)}
      onBlur={() => setOpen(false)}
    >
      {children}
    </div>
  );
};

// ── TooltipContent ───────────────────────────────────────────────────────────
interface TooltipContentProps {
  children: React.ReactNode;
  side?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
  sideOffset?: number;
}

export const TooltipContent: React.FC<TooltipContentProps> = ({
  children,
  side = 'top',
  className = '',
}) => {
  const { open } = useContext(TooltipCtx);
  if (!open) return null;

  const position: Record<string, string> = {
    top:    'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left:   'right-full top-1/2 -translate-y-1/2 mr-2',
    right:  'left-full top-1/2 -translate-y-1/2 ml-2',
  };

  const arrowPos: Record<string, string> = {
    top:    'top-[calc(100%-4px)] left-1/2 -translate-x-1/2',
    bottom: 'bottom-[calc(100%-4px)] left-1/2 -translate-x-1/2',
    left:   'left-[calc(100%-4px)] top-1/2 -translate-y-1/2',
    right:  'right-[calc(100%-4px)] top-1/2 -translate-y-1/2',
  };

  return (
    <div
      role="tooltip"
      className={`
        absolute z-50 ${position[side]}
        px-3 py-1.5 rounded-md
        text-xs font-medium text-white bg-gray-900
        shadow-md whitespace-nowrap pointer-events-none
        ${className}
      `}
      style={{ animation: 'psyTooltipIn 120ms ease-out' }}
    >
      {children}
      {/* Caret arrow */}
      <span className={`absolute w-2 h-2 bg-gray-900 rotate-45 ${arrowPos[side]}`} />
      <style>{`
        @keyframes psyTooltipIn {
          from { opacity: 0; transform: scale(0.94); }
          to   { opacity: 1; transform: scale(1);    }
        }
      `}</style>
    </div>
  );
};
