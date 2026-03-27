import { Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import LearnMore from './pages/LearnMore';
import Settings from './pages/Settings';
import History from './pages/History';
import HistoryDetail from './pages/HistoryDetail';
import { ProtectedRoute, Login } from './routes/ProtectedRoute';
import { GuestModeProvider } from './context/GuestModeContext';

function App() {
  return (
    <GuestModeProvider>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/auth" element={<Login />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/history"
          element={
            <ProtectedRoute>
              <History />
            </ProtectedRoute>
          }
        />
        <Route
          path="/history/:id"
          element={
            <ProtectedRoute>
              <HistoryDetail />
            </ProtectedRoute>
          }
        />
        <Route
          path="/settings"
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          }
        />
        <Route path="/learn-more" element={<LearnMore />} />
      </Routes>
    </GuestModeProvider>
  );
}

export default App;
