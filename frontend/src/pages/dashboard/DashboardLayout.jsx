import { Outlet, useLocation } from 'react-router-dom'
import Sidebar from '../../components/common/Sidebar'
import { useAuth } from '../../context/AuthContext'

const PAGE_TITLES = {
  '/dashboard/overview': 'Overview',
  '/dashboard/soil': 'Soil Test',
  '/dashboard/crops': 'Crop Recommendation',
  '/dashboard/fertilizer': 'Fertilizer Prescription',
  '/dashboard/yield': 'Yield Prediction',
  '/dashboard/alerts': 'Weather Alerts',
}

function initials(name) {
  if (!name) return 'F'
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}

export default function DashboardLayout() {
  const { farmer } = useAuth()
  const location = useLocation()
  const title = PAGE_TITLES[location.pathname] || 'Dashboard'

  return (
    <div className="flex h-screen overflow-hidden bg-surface">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-gray-100 bg-white px-6 py-4">
          <h1 className="text-lg font-semibold text-text-primary">{title}</h1>
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-text-secondary">{farmer?.name}</span>
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-sm font-semibold text-white">
              {initials(farmer?.name)}
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
