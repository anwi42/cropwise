import { CloudSun, Droplets, MapPin, Sprout } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import BankFarmerSearchBar from '../../../components/common/BankFarmerSearchBar'
import Badge from '../../../components/common/Badge'
import Button from '../../../components/common/Button'
import Card from '../../../components/common/Card'
import Loader from '../../../components/common/Loader'
import { CROP_LABELS, HEALTH_ZONE_VARIANT } from '../../../constants'
import { useBankAuth } from '../../../context/BankAuthContext'

function initials(name) {
  if (!name) return 'F'
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase())
    .join('')
}

function cropLabel(crop) {
  if (!crop) return crop
  return CROP_LABELS[crop] || crop.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase())
}

export default function BankVerifyPage() {
  const navigate = useNavigate()
  const { officer } = useBankAuth()
  const [profile, setProfile] = useState(null)
  const [searching, setSearching] = useState(false)

  function handleFound(data) {
    setProfile(data)
    setSearching(false)
  }

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-6">
        <BankFarmerSearchBar
          onSearchStart={() => setSearching(true)}
          onFound={handleFound}
          officerId={officer?.officerId}
        />
      </Card>

      {searching && !profile && <Loader label="Looking up farmer..." />}

      {profile && (
        <Card className="p-6">
          <div className="flex flex-wrap items-start justify-between gap-4 border-b border-gray-100 pb-4">
            <div className="flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-full bg-primary text-lg font-semibold text-white">
                {initials(profile.name)}
              </div>
              <div>
                <h2 className="text-xl font-bold text-text-primary">{profile.name}</h2>
                <p className="flex items-center gap-1 text-sm text-text-secondary">
                  <MapPin className="h-4 w-4" />
                  {[profile.village, profile.taluka, profile.district, profile.state]
                    .filter(Boolean)
                    .join(', ') || 'Location not on file'}
                </p>
                <p className="mt-1 text-xs text-text-secondary">
                  Farmer ID #{profile.farmer_id} &middot; {profile.phone}
                </p>
              </div>
            </div>
            <div className="flex flex-wrap gap-2">
              <Button
                variant="solid"
                onClick={() => navigate(`/bank/dashboard/certificate?farmer_id=${profile.farmer_id}`)}
              >
                Generate Certificate
              </Button>
              <Button
                variant="outline"
                onClick={() => navigate(`/bank/dashboard/loan?farmer_id=${profile.farmer_id}`)}
              >
                Calculate Loan Score
              </Button>
            </div>
          </div>

          <div className="grid gap-6 py-6 sm:grid-cols-2 lg:grid-cols-3">
            <div>
              <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-text-secondary">
                <Sprout className="h-4 w-4" /> Farm Details
              </h3>
              <dl className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Farm Size</dt>
                  <dd className="font-medium text-text-primary">
                    {profile.farm_size != null ? `${profile.farm_size} acres` : 'Not on file'}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Soil Type</dt>
                  <dd className="font-medium capitalize text-text-primary">
                    {profile.soil_type || 'Not on file'}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Water Source</dt>
                  <dd className="font-medium capitalize text-text-primary">
                    {profile.water_source || 'Not on file'}
                  </dd>
                </div>
              </dl>
            </div>

            <div>
              <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-text-secondary">
                <Droplets className="h-4 w-4" /> Soil Health
              </h3>
              {profile.latest_soil_report && profile.latest_soil_report.health_score != null ? (
                <div className="flex items-center gap-3">
                  <span className="text-3xl font-bold text-text-primary">
                    {profile.latest_soil_report.health_score}
                  </span>
                  <Badge variant={HEALTH_ZONE_VARIANT[profile.latest_soil_report.health_zone] || 'neutral'}>
                    {profile.latest_soil_report.health_zone} Zone
                  </Badge>
                </div>
              ) : (
                <p className="text-sm text-text-secondary">No scored soil report yet</p>
              )}
              {profile.latest_soil_report && (
                <p className="mt-2 text-xs text-text-secondary">
                  Report dated {profile.latest_soil_report.report_date}
                </p>
              )}
            </div>

            <div>
              <h3 className="mb-2 flex items-center gap-2 text-sm font-semibold text-text-secondary">
                <CloudSun className="h-4 w-4" /> Weather Alerts
              </h3>
              {profile.weather_alerts_history.length === 0 ? (
                <Badge variant="success">No alerts on record</Badge>
              ) : (
                <Badge variant="warning">
                  {profile.weather_alerts_history.length} alert
                  {profile.weather_alerts_history.length > 1 ? 's' : ''} on record
                </Badge>
              )}
            </div>
          </div>

          <div className="grid gap-6 border-t border-gray-100 pt-6 sm:grid-cols-2">
            <div>
              <h3 className="mb-2 text-sm font-semibold text-text-secondary">Latest Crop &amp; Yield Prediction</h3>
              {profile.latest_yield_prediction ? (
                <div className="rounded-lg bg-surface p-4 text-sm">
                  <p className="font-medium text-text-primary">
                    {cropLabel(profile.latest_yield_prediction.crop_type)} ({profile.latest_yield_prediction.crop_variety})
                  </p>
                  <p className="mt-1 text-text-secondary">
                    Predicted yield: {profile.latest_yield_prediction.predicted_yield_min}–
                    {profile.latest_yield_prediction.predicted_yield_max} tons/acre
                  </p>
                  <p className="text-text-secondary">
                    Confidence: {profile.latest_yield_prediction.confidence_score}%
                  </p>
                </div>
              ) : (
                <p className="text-sm text-text-secondary">No yield prediction on record</p>
              )}
            </div>

            <div>
              <h3 className="mb-2 text-sm font-semibold text-text-secondary">Crop History</h3>
              {profile.crops_grown_before && profile.crops_grown_before.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {profile.crops_grown_before.map((crop) => (
                    <Badge key={crop} variant="primary">
                      {cropLabel(crop)}
                    </Badge>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-text-secondary">No crop history recorded</p>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
