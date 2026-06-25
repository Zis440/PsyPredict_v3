import { Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import LearnMore from './pages/LearnMore';
import Settings from './pages/Settings';
import History from './pages/History';
import HistoryDetail from './pages/HistoryDetail';
import Progress from './pages/Progress';
import VisualPsychology from './pages/VisualPsychology';
import SegmentSelection from './pages/SegmentSelection';
import { ProtectedRoute, Login } from './routes/ProtectedRoute';
import { GuestModeProvider } from './context/GuestModeContext';
import { SegmentProvider } from './context/SegmentContext';
// import LevelSelection from './pages/LevelSelection';
// import AssessmentRunner from './pages/AssessmentRunner';

function App() {
  return (
    <SegmentProvider>
      <GuestModeProvider>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/auth" element={<Login />} />
          <Route path="/select-segment" element={<SegmentSelection />} />
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
          <Route
            path="/progress"
            element={
              <ProtectedRoute>
                <Progress />
              </ProtectedRoute>
            }
          />
          {/* <Route
            path="/assessments"
            element={
              <ProtectedRoute>
                <LevelSelection />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assessments/:packageId"
            element={
              <ProtectedRoute>
                <AssessmentRunner />
              </ProtectedRoute>
            }
          /> */}
          <Route
            path="/visual-psychology"
            element={
              <ProtectedRoute>
                <VisualPsychology />
              </ProtectedRoute>
            }
          />
          <Route path="/learn-more" element={<LearnMore />} />
        </Routes>
      </GuestModeProvider>
    </SegmentProvider>
  );
}

export default App;
