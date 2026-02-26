// import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import { ErrorBoundary } from './ErrorBoundary.tsx'
import './index.css'

// NOTE: React.StrictMode is intentionally removed.
// Framer Motion v12 animations freeze (opacity stays 0) when StrictMode is active
// in development, causing a completely blank white page.
ReactDOM.createRoot(document.getElementById('root')!).render(
  <ErrorBoundary>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </ErrorBoundary>,
)