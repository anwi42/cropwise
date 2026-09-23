import { CheckCircle2, CloudRain, Droplets, RefreshCw, Snowflake, Sun } from 'lucide-react'
import { useEffect, useState } from 'react'
import { toast } from 'react-toastify'
import Card from '../../components/common/Card'
import Button from '../../components/common/Button'
import Loader from '../../components/common/Loader'
import { ALERT_TYPE_META } from '../../constants'
import { useAuth } from '../../context/AuthContext'
import { getAlerts, getErrorMessage, runWeatherCheck } from '../../services/api'

const ICONS = { CloudRain, Sun, Snowflake, Droplets }

function formatTimestamp(value) {
  return new Date(value).toLocaleString('en-IN', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export default function AlertsPage() {
  const { farmer, alerts, setAlerts, alertsCheckedAt, setAlertsCheckedAt } = useAuth()
  const [loading, setLoading] = useState(false)
  const [checking, setChecking] = useState(false)

  async function fetchAlerts(merge) {
    const { data } = await getAlerts(farmer.farmerId)
    setAlerts((prev) => {
      if (!merge || !prev) return data.alerts
      const existingIds = new Set(prev.map((a) => a.id))
      return [...data.alerts.filter((a) => !existingIds.has(a.id)), ...prev]
    })
    setAlertsCheckedAt(new Date().toISOString())
  }

  useEffect(() => {
    if (alertsCheckedAt || !farmer?.farmerId) return
    setLoading(true)
    fetchAlerts(false)
      .catch((error) => toast.error(getErrorMessage(error, 'Could not load weather alerts.')))
      .finally(() => setLoading(false))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  async function handleRunCheck() {
    setChecking(true)
    try {
      const { data } = await runWeatherCheck()
      toast.success(
        `Checked ${data.farmers_checked} farmers, created ${data.alerts_created} new alert(s).`
      )
      await fetchAlerts(true)
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not run the weather check. Please try again.'))
    } finally {
      setChecking(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <Card className="flex flex-col gap-3 p-6 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <Button variant="outline" onClick={handleRunCheck} disabled={checking}>
            <RefreshCw className={`h-4 w-4 ${checking ? 'animate-spin' : ''}`} />
            {checking ? 'Checking...' : 'Run Weather Check'}
          </Button>
          <p className="mt-2 text-xs text-text-secondary">
            {alertsCheckedAt ? `Last checked: ${formatTimestamp(alertsCheckedAt)}` : 'Not checked yet'}
          </p>
        </div>
      </Card>

      {loading && <Loader label="Loading weather alerts..." />}

      {!loading && (!alerts || alerts.length === 0) && (
        <Card className="flex items-center gap-3 bg-success/10 p-6 text-success">
          <CheckCircle2 className="h-6 w-6 shrink-0" />
          <span>No weather threats detected for your farm today.</span>
        </Card>
      )}

      {!loading && alerts && alerts.length > 0 && (
        <div className="flex flex-col gap-3">
          {alerts.map((alert) => {
            const meta = ALERT_TYPE_META[alert.alert_type] || { label: alert.alert_type, icon: 'CloudRain' }
            const Icon = ICONS[meta.icon] ?? CloudRain
            return (
              <Card key={alert.id} className="flex items-start gap-3 border-l-4 border-l-primary p-4">
                <Icon className="mt-0.5 h-5 w-5 shrink-0 text-primary" />
                <div>
                  <p className="text-xs font-semibold uppercase tracking-wide text-primary">{meta.label}</p>
                  <p className="mt-1 font-medium text-text-primary">{alert.alert_message}</p>
                  <p className="mt-1 text-xs text-text-secondary">{formatTimestamp(alert.created_at)}</p>
                </div>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )
}
