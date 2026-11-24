import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './lib/auth-context';
import { RequireAuth } from './components/auth/RequireAuth';
import LoginPage from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import CockpitPage from './pages/operations/CockpitPage';
import CaseDetailPage from './pages/operations/CaseDetailPage';
import TaskQueuePage from './pages/partner/TaskQueuePage';
import TaskDetailPage from './pages/partner/TaskDetailPage';
import BagStatusPage from './pages/passenger/BagStatusPage';
import BagListPage from './pages/passenger/BagListPage';
import CaseStatusPage from './pages/passenger/CaseStatusPage';
import { OverviewPage } from './pages/executive/OverviewPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/dashboard"
            element={
              <RequireAuth>
                <DashboardPage />
              </RequireAuth>
            }
          />
          <Route
            path="/operations/cockpit"
            element={
              <RequireAuth>
                <CockpitPage />
              </RequireAuth>
            }
          />
          <Route
            path="/operations/cases/:caseId"
            element={
              <RequireAuth>
                <CaseDetailPage />
              </RequireAuth>
            }
          />
          <Route
            path="/partner/tasks"
            element={
              <RequireAuth>
                <TaskQueuePage />
              </RequireAuth>
            }
          />
          <Route
            path="/partner/tasks/:taskId"
            element={
              <RequireAuth>
                <TaskDetailPage />
              </RequireAuth>
            }
          />
          <Route
            path="/passenger/bags"
            element={
              <RequireAuth>
                <BagListPage />
              </RequireAuth>
            }
          />
          <Route
            path="/passenger/bags/:bagTag/status"
            element={
              <RequireAuth>
                <BagStatusPage />
              </RequireAuth>
            }
          />
          <Route
            path="/passenger/cases/:caseReference"
            element={
              <RequireAuth>
                <CaseStatusPage />
              </RequireAuth>
            }
          />
          <Route
            path="/executive/overview"
            element={
              <RequireAuth>
                <OverviewPage />
              </RequireAuth>
            }
          />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
