import { CloudRain, Droplets, Thermometer } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import Badge from '../../components/common/Badge'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import Input from '../../components/common/Input'
import Loader from '../../components/common/Loader'
import Select from '../../components/common/Select'
import { BUDGET_OPTIONS, CROP_LABELS, MARKET_RISK_VARIANT, SEASON_OPTIONS } from '../../constants'
import { useAuth } from '../../context/AuthContext'
import { getCropRecommendation, getErrorMessage } from '../../services/api'

const RANK_STYLES = [
  { border: 'border-yellow-400', label: '#1 Best Match' },
  { border: 'border-gray-400', label: '#2 Good Match' },
  { border: 'border-orange-700', label: '#3 Fair Match' },
]

function FitScoreRing({ score }) {
  const radius = 36
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference
  const color = score >= 70 ? 'stroke-success' : score >= 40 ? 'stroke-warning' : 'stroke-danger'

  return (
    <div className="relative flex h-24 w-24 items-center justify-center">
      <svg className="h-24 w-24 -rotate-90" viewBox="0 0 84 84">
        <circle cx="42" cy="42" r={radius} strokeWidth="8" className="fill-none stroke-gray-100" />
        <circle
          cx="42"
          cy="42"
          r={radius}
          strokeWidth="8"
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className={`fill-none ${color}`}
        />
      </svg>
      <span className="absolute text-lg font-bold text-text-primary">{score}</span>
    </div>
  )
}

export default function CropRecommendPage() {
  const { farmer, soilReport, cropRecommendation, setCropRecommendation } = useAuth()
  const [season, setSeason] = useState(cropRecommendation?.season || '')
  const [budget, setBudget] = useState('')
  const [cropPreference, setCropPreference] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    if (!season) {
      toast.error('Please select a season.')
      return
    }
    setLoading(true)
    try {
      const { data } = await getCropRecommendation({
        farmer_id: farmer.farmerId,
        soil_report_id: soilReport.id,
        season,
        budget: budget || undefined,
        crop_preference: cropPreference.trim() || undefined,
      })
      setCropRecommendation({
        season: data.season,
        weather: data.weather,
        recommendations: data.recommendations,
      })
      toast.success('Crop recommendations ready.')
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not fetch crop recommendations. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  if (!soilReport) {
    return (
      <Card className="p-8 text-center">
        <p className="text-text-secondary">
          You need a soil report before we can recommend crops.{' '}
          <Link to="/dashboard/soil" className="font-medium text-primary hover:underline">
            Take a soil test first
          </Link>
          .
        </p>
      </Card>
    )
  }

  const recommendations = cropRecommendation?.recommendations
  const weather = cropRecommendation?.weather

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Select
              label="Season"
              placeholder="Select season"
              options={SEASON_OPTIONS}
              value={season}
              onChange={(e) => setSeason(e.target.value)}
            />
            <Select
              label="Budget for Inputs"
              placeholder="Select budget"
              options={BUDGET_OPTIONS}
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
            />
            <Input
              label="Crop Preference"
              placeholder="Do you have a crop in mind? (optional)"
              value={cropPreference}
              onChange={(e) => setCropPreference(e.target.value)}
            />
          </div>
          <div>
            <Button type="submit" disabled={loading}>
              {loading ? 'Analyzing...' : 'Get Recommendations'}
            </Button>
          </div>
        </form>
        <p className="mt-3 text-xs text-text-secondary">
          Uses your latest soil report (saved {soilReport.reportDate}) automatically.
        </p>
      </Card>

      {loading && <Loader label="Analyzing soil and weather data..." />}

      {!loading && recommendations && (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {recommendations.map((rec, idx) => (
              <Card key={rec.crop_name} className={`border-2 p-5 ${RANK_STYLES[idx]?.border ?? 'border-gray-100'}`}>
                <p className="text-xs font-semibold uppercase tracking-wide text-text-secondary">
                  {RANK_STYLES[idx]?.label ?? `#${idx + 1}`}
                </p>
                <h3 className="mt-1 text-xl font-bold text-text-primary">
                  {CROP_LABELS[rec.crop_name] ?? rec.crop_name}
                </h3>
                <div className="mt-4 flex items-center justify-between gap-4">
                  <FitScoreRing score={rec.soil_fit_score} />
                  <Badge variant={MARKET_RISK_VARIANT[rec.market_risk] ?? 'neutral'}>
                    {rec.market_risk} risk
                  </Badge>
                </div>
                <p className="mt-4 text-sm text-text-secondary">{rec.reasoning}</p>
              </Card>
            ))}
          </div>

          {weather && (
            <Card className="p-5">
              <h3 className="mb-3 font-semibold text-text-primary">Weather Used For This Recommendation</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="flex items-center gap-3">
                  <CloudRain className="h-5 w-5 text-primary" />
                  <div>
                    <p className="text-sm text-text-secondary">Rainfall (14-day forecast)</p>
                    <p className="font-semibold text-text-primary">{weather.rainfall_mm} mm</p>
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Thermometer className="h-5 w-5 text-primary" />
                  <div>
                    <p className="text-sm text-text-secondary">Average Temperature</p>
                    <p className="font-semibold text-text-primary">{weather.avg_temperature_c} °C</p>
                  </div>
                </div>
              </div>
              {weather.fallback_used && weather.warning && (
                <p className="mt-3 flex items-center gap-2 text-xs text-warning">
                  <Droplets className="h-4 w-4" />
                  {weather.warning}
                </p>
              )}
            </Card>
          )}
        </>
      )}
    </div>
  )
}
