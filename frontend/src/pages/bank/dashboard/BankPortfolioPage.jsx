import 'leaflet/dist/leaflet.css'
import { useEffect, useMemo, useState } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer } from 'react-leaflet'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import Badge from '../../../components/common/Badge'
import Card from '../../../components/common/Card'
import Loader from '../../../components/common/Loader'
import Select from '../../../components/common/Select'
import { useBankAuth } from '../../../context/BankAuthContext'
import { getBankPortfolio, getErrorMessage } from '../../../services/api'

const INDIA_CENTER = [22.9734, 78.6569]

const RISK_COLOR = {
  LOW: '#10b981',
  MEDIUM: '#f59e0b',
  HIGH: '#ef4444',
}

const RISK_BADGE_VARIANT = {
  LOW: 'success',
  MEDIUM: 'warning',
  HIGH: 'danger',
}

function riskReason(farmer) {
  const reasons = []
  if (farmer.soil_health_zone === 'Red' || farmer.soil_health_zone == null) {
    reasons.push(farmer.soil_health_zone == null ? 'soil not scored' : 'soil health is Red')
  } else if (farmer.soil_health_zone === 'Yellow') {
    reasons.push('soil health is Yellow')
  }
  if (farmer.active_weather_alerts >= 2) reasons.push(`${farmer.active_weather_alerts} active weather alerts`)
  else if (farmer.active_weather_alerts === 1) reasons.push('1 active weather alert')
  if (!farmer.crop_type) reasons.push('no yield data')
  return reasons.length > 0 ? reasons.join(', ') : 'good soil health, no alerts, healthy yield data'
}

export default function BankPortfolioPage() {
  const { officer } = useBankAuth()
  const navigate = useNavigate()
  const [farmers, setFarmers] = useState([])
  const [loading, setLoading] = useState(true)
  const [districtFilter, setDistrictFilter] = useState('')
  const [cropFilter, setCropFilter] = useState('')
  const [riskFilter, setRiskFilter] = useState('')

  useEffect(() => {
    setLoading(true)
    getBankPortfolio(officer.officerId)
      .then(({ data }) => setFarmers(data.farmers))
      .catch((error) => toast.error(getErrorMessage(error, 'Could not load portfolio.')))
      .finally(() => setLoading(false))
  }, [officer.officerId])

  const districtOptions = useMemo(
    () =>
      [...new Set(farmers.map((f) => f.district).filter(Boolean))]
        .sort()
        .map((d) => ({ value: d, label: d })),
    [farmers]
  )
  const cropOptions = useMemo(
    () =>
      [...new Set(farmers.map((f) => f.crop_type).filter(Boolean))]
        .sort()
        .map((c) => ({ value: c, label: c })),
    [farmers]
  )

  const filtered = useMemo(
    () =>
      farmers.filter((f) => {
        if (districtFilter && f.district !== districtFilter) return false
        if (cropFilter && f.crop_type !== cropFilter) return false
        if (riskFilter && f.risk_level !== riskFilter) return false
        return true
      }),
    [farmers, districtFilter, cropFilter, riskFilter]
  )

  const lowCount = filtered.filter((f) => f.risk_level === 'LOW').length
  const mediumCount = filtered.filter((f) => f.risk_level === 'MEDIUM').length
  const highCount = filtered.filter((f) => f.risk_level === 'HIGH').length

  if (loading) return <Loader label="Loading portfolio..." />

  if (farmers.length === 0) {
    return (
      <Card className="p-8 text-center">
        <p className="text-text-secondary">
          You have not verified any farmers yet. Generate a certificate, calculate a loan score, or verify
          a claim to add farmers to your portfolio.
        </p>
      </Card>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-4">
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
          <Select
            label="District"
            placeholder="All districts"
            options={districtOptions}
            value={districtFilter}
            onChange={(e) => setDistrictFilter(e.target.value)}
          />
          <Select
            label="Crop Type"
            placeholder="All crops"
            options={cropOptions}
            value={cropFilter}
            onChange={(e) => setCropFilter(e.target.value)}
          />
          <Select
            label="Risk Level"
            placeholder="All risk levels"
            options={[
              { value: 'LOW', label: 'Low' },
              { value: 'MEDIUM', label: 'Medium' },
              { value: 'HIGH', label: 'High' },
            ]}
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
          />
        </div>
      </Card>

      <Card className="overflow-hidden p-0">
        <MapContainer center={INDIA_CENTER} zoom={5} style={{ height: '480px', width: '100%' }}>
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          {filtered
            .filter((f) => f.latitude != null && f.longitude != null)
            .map((f) => (
              <CircleMarker
                key={f.farmer_id}
                center={[f.latitude, f.longitude]}
                radius={10}
                pathOptions={{
                  color: RISK_COLOR[f.risk_level],
                  fillColor: RISK_COLOR[f.risk_level],
                  fillOpacity: 0.8,
                }}
              >
                <Popup>
                  <div className="flex flex-col gap-1 text-sm">
                    <span className="font-semibold">{f.name}</span>
                    <span className="text-text-secondary">
                      {f.crop_type || 'No crop on file'} &middot; {f.district}
                    </span>
                    <span className="text-text-secondary">Risk: {riskReason(f)}</span>
                    <div className="mt-2 flex gap-2">
                      <button
                        type="button"
                        className="rounded bg-primary px-2 py-1 text-xs font-medium text-white"
                        onClick={() => navigate(`/bank/dashboard/verify`)}
                      >
                        View Profile
                      </button>
                      <button
                        type="button"
                        className="rounded border border-primary px-2 py-1 text-xs font-medium text-primary"
                        onClick={() => navigate(`/bank/dashboard/loan?farmer_id=${f.farmer_id}`)}
                      >
                        Loan Score
                      </button>
                    </div>
                  </div>
                </Popup>
              </CircleMarker>
            ))}
        </MapContainer>
      </Card>

      <Card className="p-6">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-text-primary">{filtered.length}</p>
            <p className="text-xs text-text-secondary">Total Farmers</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-success">{lowCount}</p>
            <Badge variant="success">Low Risk</Badge>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-warning">{mediumCount}</p>
            <Badge variant="warning">Medium Risk</Badge>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-danger">{highCount}</p>
            <Badge variant="danger">High Risk</Badge>
          </div>
        </div>
      </Card>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="text-text-secondary">
              <th className="pb-2 pr-4">Farmer</th>
              <th className="pb-2 pr-4">District</th>
              <th className="pb-2 pr-4">Crop</th>
              <th className="pb-2 pr-4">Soil Health</th>
              <th className="pb-2 pr-4">Alerts</th>
              <th className="pb-2">Risk</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((f, idx) => (
              <tr key={f.farmer_id} className={idx % 2 === 1 ? 'bg-surface' : ''}>
                <td className="py-2 pr-4 font-medium text-text-primary">{f.name}</td>
                <td className="py-2 pr-4 text-text-secondary">{f.district || '—'}</td>
                <td className="py-2 pr-4 capitalize text-text-secondary">{f.crop_type || 'No data'}</td>
                <td className="py-2 pr-4 text-text-secondary">
                  {f.soil_health_score != null ? `${f.soil_health_score} (${f.soil_health_zone})` : 'Not scored'}
                </td>
                <td className="py-2 pr-4 text-text-secondary">{f.active_weather_alerts}</td>
                <td className="py-2">
                  <Badge variant={RISK_BADGE_VARIANT[f.risk_level]}>{f.risk_level}</Badge>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
