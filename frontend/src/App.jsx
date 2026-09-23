import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import { AuthProvider, useAuth } from './context/AuthContext'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import DashboardLayout from './pages/dashboard/DashboardLayout'
import Overview from './pages/dashboard/Overview'
import SoilTestPage from './pages/dashboard/SoilTestPage'
import CropRecommendPage from './pages/dashboard/CropRecommendPage'
import FertilizerPage from './pages/dashboard/FertilizerPage'
import YieldPage from './pages/dashboard/YieldPage'
import OrchardAdvisoryPage from './pages/dashboard/OrchardAdvisoryPage'
import AlertsPage from './pages/dashboard/AlertsPage'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="overview" replace />} />
        <Route path="overview" element={<Overview />} />
        <Route path="soil" element={<SoilTestPage />} />
        <Route path="crops" element={<CropRecommendPage />} />
        <Route path="fertilizer" element={<FertilizerPage />} />
        <Route path="yield" element={<YieldPage />} />
        <Route path="orchard" element={<OrchardAdvisoryPage />} />
        <Route path="alerts" element={<AlertsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <ToastContainer position="top-right" autoClose={4000} />
      </AuthProvider>
    </BrowserRouter>
  )
}
