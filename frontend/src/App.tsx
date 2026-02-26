import { Link, Navigate, Route, Routes } from 'react-router-dom';
import DashboardPage from './pages/DashboardPage';
import IncomeModelPage from './pages/IncomeModelPage';
import LogActionPage from './pages/LogActionPage';
import LogExposurePage from './pages/LogExposurePage';

export default function App() {
  return (
    <div className="app-shell">
      <header>
        <h1>Optionality Tracker</h1>
        <nav>
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/income-model">Income Model</Link>
          <Link to="/log-action">Log Action</Link>
          <Link to="/log-exposure">Log Exposure</Link>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/income-model" element={<IncomeModelPage />} />
          <Route path="/log-action" element={<LogActionPage />} />
          <Route path="/log-exposure" element={<LogExposurePage />} />
        </Routes>
      </main>
    </div>
  );
}
