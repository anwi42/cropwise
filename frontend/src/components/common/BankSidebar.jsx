import {
  ChevronLeft,
  ChevronRight,
  FileCheck2,
  Home,
  Landmark,
  LogOut,
  Map,
  Search,
  ShieldAlert,
  TrendingUp,
} from 'lucide-react'
import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useBankAuth } from '../../context/BankAuthContext'

const NAV_ITEMS = [
  { to: '/bank/dashboard/overview', label: 'Overview', icon: Home },
  { to: '/bank/dashboard/verify', label: 'Farm Verification', icon: Search },
  { to: '/bank/dashboard/certificate', label: 'Yield Certificate', icon: FileCheck2 },
  { to: '/bank/dashboard/loan', label: 'Loan Score', icon: TrendingUp },
  { to: '/bank/dashboard/claim', label: 'Claim Verification', icon: ShieldAlert },
  { to: '/bank/dashboard/portfolio', label: 'Portfolio Map', icon: Map },
]

function readStoredCollapsed() {
  return localStorage.getItem('bank_sidebar_collapsed') === 'true'
}

export default function BankSidebar() {
  const { officer, logout } = useBankAuth()
  const navigate = useNavigate()
  const [collapsed, setCollapsed] = useState(readStoredCollapsed)

  function handleLogout() {
    logout()
    navigate('/bank/login')
  }

  function toggleCollapsed() {
    setCollapsed((prev) => {
      const next = !prev
      localStorage.setItem('bank_sidebar_collapsed', String(next))
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
        <Landmark className="h-7 w-7 shrink-0 text-primary" />
        {!collapsed && <span className="text-lg font-bold text-text-primary">CropWise</span>}
      </div>

      {!collapsed && (
        <div className="px-4 pb-4 text-sm font-medium text-text-secondary">
          {officer?.name || 'Bank Officer'}
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
