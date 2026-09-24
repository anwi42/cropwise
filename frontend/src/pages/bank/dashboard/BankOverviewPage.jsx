import { AlertTriangle, FileCheck2, Map, Search, ShieldAlert, TrendingUp, Users } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Button from '../../../components/common/Button'
import Card from '../../../components/common/Card'
import { useBankAuth } from '../../../context/BankAuthContext'
import { getBankOverview } from '../../../services/api'

const FEATURES = [
  {
    to: '/bank/dashboard/verify',
    icon: Search,
    title: 'Farm Verification',
    description: 'Look up a farmer and review their complete verified farm profile',
  },
  {
    to: '/bank/dashboard/certificate',
    icon: FileCheck2,
    title: 'Yield Certificate',
    description: 'Generate a signed, QR-verifiable yield certificate PDF',
  },
  {
    to: '/bank/dashboard/loan',
    icon: TrendingUp,
    title: 'Loan Score',
    description: 'Calculate a fresh loan eligibility score out of 100',
  },
  {
    to: '/bank/dashboard/claim',
    icon: ShieldAlert,
    title: 'Claim Verification',
    description: 'Check a crop loss claim against real weather records',
  },
  {
    to: '/bank/dashboard/portfolio',
    icon: Map,
    title: 'Portfolio Map',
    description: 'Monitor every farmer you have verified on one risk map',
  },
]

function greeting() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good Morning'
  if (hour < 17) return 'Good Afternoon'
  return 'Good Evening'
}

export default function BankOverviewPage() {
  const { officer } = useBankAuth()
  const [stats, setStats] = useState(null)

  useEffect(() => {
    getBankOverview(officer.officerId)
      .then(({ data }) => setStats(data))
      .catch(() => {})
  }, [officer.officerId])

  return (
    <div className="flex flex-col gap-6">
      <Card className="bg-gradient-to-r from-primary to-primary-dark p-8 text-white">
        <h1 className="text-2xl font-bold">
          {greeting()}, {officer?.name || 'Officer'}
        </h1>
        <p className="mt-1 text-primary-light">Here&apos;s your risk intelligence snapshot for today</p>
      </Card>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="p-5">
          <div className="flex items-center gap-2 text-text-secondary">
            <Users className="h-4 w-4" />
            <span className="text-sm font-medium">Total Farmers Verified</span>
          </div>
          <p className="mt-3 text-3xl font-bold text-text-primary">
            {stats ? stats.total_farmers_verified : '…'}
          </p>
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-2 text-text-secondary">
            <FileCheck2 className="h-4 w-4" />
            <span className="text-sm font-medium">Certificates Today</span>
          </div>
          <p className="mt-3 text-3xl font-bold text-text-primary">
            {stats ? stats.certificates_today : '…'}
          </p>
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-2 text-text-secondary">
            <AlertTriangle className="h-4 w-4" />
            <span className="text-sm font-medium">High Risk Farmers</span>
          </div>
          <p className="mt-3 text-3xl font-bold text-danger">{stats ? stats.high_risk_farmers : '…'}</p>
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-2 text-text-secondary">
            <ShieldAlert className="h-4 w-4" />
            <span className="text-sm font-medium">Pending Claim Reviews</span>
          </div>
          <p className="mt-3 text-3xl font-bold text-warning">
            {stats ? stats.pending_claim_verifications : '…'}
          </p>
        </Card>
      </div>

      <div>
        <h2 className="mb-3 text-base font-semibold text-text-primary">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(({ to, icon: Icon, title, description }) => (
            <Card key={title} className="flex flex-col gap-3 p-5">
              <Icon className="h-8 w-8 text-primary" />
              <h3 className="font-bold text-text-primary">{title}</h3>
              <p className="flex-1 text-sm text-text-secondary">{description}</p>
              <Link to={to}>
                <Button variant="outline" className="w-full">
                  Open
                </Button>
              </Link>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
