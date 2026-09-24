import { Outlet, useLocation } from 'react-router-dom'
import BankSidebar from '../../../components/common/BankSidebar'
import { useBankAuth } from '../../../context/BankAuthContext'

const PAGE_TITLES = {
  '/bank/dashboard/overview': 'Overview',
  '/bank/dashboard/verify': 'Farm Verification',
  '/bank/dashboard/certificate': 'Yield Certificate',
  '/bank/dashboard/loan': 'Loan Score',
  '/bank/dashboard/claim': 'Claim Verification',
  '/bank/dashboard/portfolio': 'Portfolio Map',
}

function initials(name) {
  if (!name) return 'B'
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}

export default function BankDashboardLayout() {
  const { officer } = useBankAuth()
  const location = useLocation()
  const title = PAGE_TITLES[location.pathname] || 'Dashboard'

  return (
    <div className="flex h-screen overflow-hidden bg-surface">
      <BankSidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between border-b border-gray-100 bg-white px-6 py-4">
          <h1 className="text-lg font-semibold text-text-primary">{title}</h1>
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-text-secondary">{officer?.name}</span>
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-sm font-semibold text-white">
              {initials(officer?.name)}
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
