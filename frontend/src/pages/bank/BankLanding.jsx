import { Activity, ShieldCheck, TrendingUp } from 'lucide-react'
import { Link } from 'react-router-dom'
import BankNavbar from '../../components/common/BankNavbar'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'

const FEATURES = [
  {
    icon: ShieldCheck,
    title: 'Instant Farm Verification',
    description: 'Look up any farmer by phone number and see their verified farm, soil and crop profile in seconds.',
  },
  {
    icon: TrendingUp,
    title: 'AI Powered Loan Scoring',
    description: 'Get a data-backed loan eligibility score out of 100, with a recommended loan amount range.',
  },
  {
    icon: Activity,
    title: 'Real Time Portfolio Monitoring',
    description: 'Track every farmer you have verified on one risk map, updated as conditions change.',
  },
]

export default function BankLanding() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      <BankNavbar />

      <section className="bg-primary-light px-6 py-24 text-center">
        <h1 className="mx-auto max-w-3xl text-4xl font-bold text-text-primary sm:text-5xl">
          Agricultural Risk Intelligence
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-text-secondary">
          Verify farms, assess loan risk and monitor your portfolio with AI
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <Link to="/bank/login">
            <Button variant="solid" className="px-8 py-3 text-base">
              Login
            </Button>
          </Link>
          <Link to="/bank/register">
            <Button variant="outline" className="px-8 py-3 text-base">
              Register
            </Button>
          </Link>
        </div>
      </section>

      <section className="mx-auto grid w-full max-w-6xl gap-6 px-6 py-16 sm:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, description }) => (
          <Card key={title} className="p-6 text-left">
            <Icon className="h-9 w-9 text-primary" />
            <h3 className="mt-4 text-lg font-semibold text-text-primary">{title}</h3>
            <p className="mt-2 text-sm text-text-secondary">{description}</p>
          </Card>
        ))}
      </section>

      <footer className="mt-auto border-t border-gray-100 py-6 text-center text-sm text-text-secondary">
        CropWise © 2026
      </footer>
    </div>
  )
}
