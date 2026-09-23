import {
  BarChart3,
  ChevronLeft,
  ChevronRight,
  CloudSun,
  FlaskConical,
  Home,
  Leaf,
  LogOut,
  Sprout,
  TreeDeciduous,
  Wheat,
} from 'lucide-react'
import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

const NAV_ITEMS = [
  { to: '/dashboard/overview', label: 'Overview', icon: Home },
  { to: '/dashboard/soil', label: 'Soil Test', icon: Sprout },
  { to: '/dashboard/crops', label: 'Crop Recommendation', icon: Wheat },
  { to: '/dashboard/fertilizer', label: 'Fertilizer Prescription', icon: FlaskConical },
  { to: '/dashboard/yield', label: 'Yield Prediction', icon: BarChart3 },
  { to: '/dashboard/orchard', label: 'Orchard Advisory', icon: TreeDeciduous },
  { to: '/dashboard/alerts', label: 'Weather Alerts', icon: CloudSun },
]

function readStoredCollapsed() {
  return localStorage.getItem('sidebar_collapsed') === 'true'
}

export default function Sidebar() {
  const { farmer, logout } = useAuth()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(readStoredCollapsed)

  function handleLogout() {
    logout()
    navigate('/login')
  }

  function toggleCollapsed() {
    setCollapsed((prev) => {
      const next = !prev
      localStorage.setItem('sidebar_collapsed', String(next))
      return next
    })
  }

  return (
    <aside
      className={`relative flex h-screen flex-col border-r border-gray-100 bg-white transition-all duration-300 ${
        collapsed ? 'w-[70px]' : 'w-[260px]'
      }`}
    >
      <button
        type="button"
        onClick={toggleCollapsed}
        title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
        className="absolute -right-3 top-8 flex h-6 w-6 items-center justify-center rounded-full border border-gray-200 bg-white text-text-secondary shadow-sm hover:text-primary"
      >
        {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
      </button>

      <div className={`flex items-center gap-2 px-4 py-5 ${collapsed ? 'justify-center px-0' : ''}`}>
        <Leaf className="h-7 w-7 shrink-0 text-primary" />
        {!collapsed && <span className="text-lg font-bold text-text-primary">CropWise</span>}
      </div>

      {!collapsed && (
        <div className="px-4 pb-4 text-sm font-medium text-text-secondary">
          {farmer?.name || 'Farmer'}
        </div>
      )}

      <nav className="flex flex-1 flex-col gap-1 px-2">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            title={collapsed ? label : undefined}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                collapsed ? 'justify-center' : ''
              } ${
                isActive
                  ? 'bg-primary text-white'
                  : 'text-text-secondary hover:bg-primary-light hover:text-primary'
              }`
            }
          >
            <Icon className="h-5 w-5 shrink-0" />
            {!collapsed && <span>{label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-gray-100 p-2">
        <button
          type="button"
          onClick={handleLogout}
          title={collapsed ? 'Logout' : undefined}
          className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-danger hover:bg-danger/10 ${
            collapsed ? 'justify-center' : ''
          }`}
        >
          <LogOut className="h-5 w-5 shrink-0" />
          {!collapsed && <span>Logout</span>}
        </button>
      </div>
    </aside>
  )
}
