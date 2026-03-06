import ReactDOM from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { ConvexReactClient } from "convex/react";
import { ConvexAuthProvider } from "@convex-dev/auth/react";
import App from './App.tsx'
import { ErrorBoundary } from './ErrorBoundary.tsx'
import './index.css'

const convex = new ConvexReactClient(import.meta.env.VITE_CONVEX_URL as string);

// NOTE: React.StrictMode is intentionally removed.
// Framer Motion v12 animations freeze (opacity stays 0) when StrictMode is active
// in development, causing a completely blank white page.
ReactDOM.createRoot(document.getElementById('root')!).render(
  <ErrorBoundary>
    <ConvexAuthProvider client={convex}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </ConvexAuthProvider>
  </ErrorBoundary>,
)