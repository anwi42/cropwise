import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { ToastContainer } from 'react-toastify'
import 'react-toastify/dist/ReactToastify.css'
import { AuthProvider, useAuth } from './context/AuthContext'
import { BankAuthProvider, useBankAuth } from './context/BankAuthContext'
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
import BankLanding from './pages/bank/BankLanding'
import BankLogin from './pages/bank/BankLogin'
import BankRegister from './pages/bank/BankRegister'
import BankDashboardLayout from './pages/bank/dashboard/BankDashboardLayout'
import BankOverviewPage from './pages/bank/dashboard/BankOverviewPage'
import BankVerifyPage from './pages/bank/dashboard/BankVerifyPage'
import BankCertificatePage from './pages/bank/dashboard/BankCertificatePage'
import BankLoanPage from './pages/bank/dashboard/BankLoanPage'
import BankClaimPage from './pages/bank/dashboard/BankClaimPage'
import BankPortfolioPage from './pages/bank/dashboard/BankPortfolioPage'
import CertificateVerify from './pages/bank/CertificateVerify'

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth()
  if (!isAuthenticated) return <Navigate to="/login" replace />
  return children
}

function BankProtectedRoute({ children }) {
  const { isAuthenticated } = useBankAuth()
  if (!isAuthenticated) return <Navigate to="/bank/login" replace />
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

      <Route path="/bank" element={<BankLanding />} />
      <Route path="/bank/login" element={<BankLogin />} />
      <Route path="/bank/register" element={<BankRegister />} />
      <Route
        path="/bank/dashboard"
        element={
          <BankProtectedRoute>
            <BankDashboardLayout />
          </BankProtectedRoute>
        }
      >
        <Route index element={<Navigate to="overview" replace />} />
        <Route path="overview" element={<BankOverviewPage />} />
        <Route path="verify" element={<BankVerifyPage />} />
        <Route path="certificate" element={<BankCertificatePage />} />
        <Route path="loan" element={<BankLoanPage />} />
        <Route path="claim" element={<BankClaimPage />} />
        <Route path="portfolio" element={<BankPortfolioPage />} />
      </Route>

      <Route path="/bank/verify/:code" element={<CertificateVerify />} />

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <BankAuthProvider>
          <AppRoutes />
          <ToastContainer position="top-right" autoClose={4000} />
        </BankAuthProvider>
      </AuthProvider>
    </BrowserRouter>
  )
}
