// src/ErrorBoundary.tsx
// Catches runtime render errors and surfaces them instead of showing a blank page
import React from 'react';

interface State { hasError: boolean; error?: Error }

export class ErrorBoundary extends React.Component<{ children: React.ReactNode }, State> {
    constructor(props: { children: React.ReactNode }) {
        super(props);
        this.state = { hasError: false };
    }

    static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    componentDidCatch(error: Error, info: React.ErrorInfo) {
        console.error('PsyPredict render error:', error, info);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div style={{ padding: '2rem', fontFamily: 'monospace', color: '#b91c1c', background: '#fef2f2', minHeight: '100vh' }}>
                    <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>⚠️ PsyPredict — Render Error</h1>
                    <p style={{ marginTop: '1rem', color: '#374151' }}>
                        The app crashed during rendering. Please check the browser console (F12) for details.
                    </p>
                    <pre style={{ marginTop: '1rem', background: '#fff', padding: '1rem', borderRadius: '0.5rem', border: '1px solid #fca5a5', fontSize: '0.85rem', overflowX: 'auto' }}>
                        {this.state.error?.toString()}
                    </pre>
                    <button
                        onClick={() => window.location.reload()}
                        style={{ marginTop: '1rem', background: '#4f46e5', color: 'white', padding: '0.5rem 1rem', border: 'none', borderRadius: '0.5rem', cursor: 'pointer' }}
                    >
                        Reload Page
                    </button>
                </div>
            );
        }
        return this.props.children;
    }
}
