import { BarChart3, Bell, CalendarDays, CloudSun, FileText, FlaskConical, Sprout, Wheat } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import Badge from '../../components/common/Badge'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import { useAuth } from '../../context/AuthContext'
import { HEALTH_ZONE_VARIANT } from '../../constants'
import { getAlerts } from '../../services/api'

const FEATURES = [
  {
    to: '/dashboard/soil',
    icon: Sprout,
    title: 'Soil Test',
    description: 'Upload your soil report or enter manually',
  },
  {
    to: '/dashboard/crops',
    icon: Wheat,
    title: 'Crop Recommendation',
    description: 'Get AI powered crop suggestions for this season',
  },
  {
    to: '/dashboard/fertilizer',
    icon: FlaskConical,
    title: 'Fertilizer Prescription',
    description: 'Know exactly what and how much to apply',
  },
  {
    to: '/dashboard/yield',
    icon: BarChart3,
    title: 'Yield Prediction',
    description: 'Predict your harvest 6-8 weeks in advance',
  },
  {
    to: '/dashboard/alerts',
    icon: CloudSun,
    title: 'Weather Alerts',
    description: 'Stay ahead of dangerous weather patterns',
  },
  {
    to: '/dashboard/fertilizer',
    icon: FileText,
    title: 'Download Reports',
    description: 'Download your soil and yield reports as PDF',
  },
]

function greeting() {
  const hour = new Date().getHours()
  if (hour < 12) return 'Good Morning'
  if (hour < 17) return 'Good Afternoon'
  return 'Good Evening'
}

export default function Overview() {
  const { farmer, soilReport, soilScore, yieldPrediction, alerts, alertsCheckedAt, setAlerts, setAlertsCheckedAt } =
    useAuth()
  const [loadingAlerts, setLoadingAlerts] = useState(false)

  useEffect(() => {
    if (alertsCheckedAt || !farmer?.farmerId) return
    setLoadingAlerts(true)
    getAlerts(farmer.farmerId)
      .then(({ data }) => {
        setAlerts(data.alerts)
        setAlertsCheckedAt(new Date().toISOString())
      })
      .catch(() => {})
      .finally(() => setLoadingAlerts(false))
  }, [alertsCheckedAt, farmer?.farmerId, setAlerts, setAlertsCheckedAt])

  const alertCount = alerts?.length ?? 0

  return (
    <div className="flex flex-col gap-6">
      <Card className="bg-gradient-to-r from-primary to-primary-dark p-8 text-white">
        <h1 className="text-2xl font-bold">
          {greeting()}, {farmer?.name || 'Farmer'} 👋
        </h1>
        <p className="mt-1 text-primary-light">Here&apos;s what&apos;s happening on your farm today</p>
      </Card>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card className="p-5">
          <div className="flex items-center gap-2 text-text-secondary">
            <Sprout className="h-4 w-4" />
            <span className="text-sm font-medium">Soil Health Score</span>
          </div>
          {soilScore ? (
            <div className="mt-3 flex items-center gap-2">
              <span className="text-3xl font-bold text-text-primary">{soilScore.score}</span>
              <span className="text-text-secondary">/100</span>
              <Badge variant={HEALTH_ZONE_VARIANT[soilScore.zone] ?? 'neutral'}>{soilScore.zone}</Badge>
            </div>
          ) : (
            <p className="mt-3 text-sm text-text-secondary">
              <Link to="/dashboard/soil" className="font-medium text-primary hover:underline">
                Take a soil test
              </Link>{' '}
              to see your score
            </p>
          )}
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-2 text-text-secondary">
            <BarChart3 className="h-4 w-4" />
            <span className="text-sm font-medium">Last Yield Prediction</span>
          </div>
          {yieldPrediction ? (
            <div className="mt-3 text-2xl font-bold text-text-primary">
              {yieldPrediction.min}&ndash;{yieldPrediction.max}{' '}
              <span className="text-sm font-normal text-text-secondary">tons/acre</span>
            </div>
          ) : (
            <p className="mt-3 text-sm text-text-secondary">
              <Link to="/dashboard/yield" className="font-medium text-primary hover:underline">
                Predict your yield
              </Link>
            </p>
          )}
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-2 text-text-secondary">
            <Bell className="h-4 w-4" />
            <span className="text-sm font-medium">Weather Alerts</span>
          </div>
          <div className="mt-3 flex items-center gap-2">
            <span className="text-3xl font-bold text-text-primary">{loadingAlerts ? '…' : alertCount}</span>
            {alertCount > 0 && <Badge variant="danger">New</Badge>}
          </div>
        </Card>

        <Card className="p-5">
          <div className="flex items-center gap-2 text-text-secondary">
            <CalendarDays className="h-4 w-4" />
            <span className="text-sm font-medium">Last Soil Test Date</span>
          </div>
          {soilReport?.reportDate ? (
            <p className="mt-3 text-2xl font-bold text-text-primary">{soilReport.reportDate}</p>
          ) : (
            <p className="mt-3 text-sm text-text-secondary">No soil report yet</p>
          )}
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
