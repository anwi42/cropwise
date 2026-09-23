import { CloudRain, Droplets, Sprout, Thermometer } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import Input from '../../components/common/Input'
import Loader from '../../components/common/Loader'
import Select from '../../components/common/Select'
import { CROP_OPTIONS } from '../../constants'
import { useAuth } from '../../context/AuthContext'
import { getErrorMessage, predictYield } from '../../services/api'

const EMPTY_FORM = { crop_type: '', crop_variety: '', sowing_date: '' }

export default function YieldPage() {
  const { farmer, soilReport, setYieldPrediction } = useAuth()
  const [form, setForm] = useState(EMPTY_FORM)
  const [errors, setErrors] = useState({})
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function validate() {
    const next = {}
    if (!form.crop_type) next.crop_type = 'Select a crop'
    if (!form.crop_variety.trim()) next.crop_variety = 'Enter the crop variety'
    if (!form.sowing_date) next.sowing_date = 'Select the sowing date'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!validate()) return

    setLoading(true)
    setResult(null)
    try {
      const { data } = await predictYield({
        farmer_id: farmer.farmerId,
        crop_type: form.crop_type,
        crop_variety: form.crop_variety.trim(),
        sowing_date: form.sowing_date,
      })
      setResult(data)
      setYieldPrediction({
        min: data.predicted_yield_min,
        max: data.predicted_yield_max,
        confidence: data.confidence_score,
      })
      toast.success('Yield prediction ready.')
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not predict yield. Please check your details and try again.'))
    } finally {
      setLoading(false)
    }
  }

  if (!soilReport) {
    return (
      <Card className="p-8 text-center">
        <p className="text-text-secondary">
          You need a soil report before we can predict your yield.{' '}
          <Link to="/dashboard/soil" className="font-medium text-primary hover:underline">
            Take a soil test first
          </Link>
          .
        </p>
      </Card>
    )
  }

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-6">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Select
            label="Crop Type"
            placeholder="Select crop"
            options={CROP_OPTIONS}
            value={form.crop_type}
            onChange={(e) => updateField('crop_type', e.target.value)}
            error={errors.crop_type}
          />
          <Input
            label="Crop Variety"
            value={form.crop_variety}
            onChange={(e) => updateField('crop_variety', e.target.value)}
            error={errors.crop_variety}
          />
          <Input
            label="Sowing Date"
            type="date"
            value={form.sowing_date}
            onChange={(e) => updateField('sowing_date', e.target.value)}
            error={errors.sowing_date}
          />
          <div className="flex items-end">
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? 'Predicting...' : 'Predict Yield'}
            </Button>
          </div>
        </form>
      </Card>

      {loading && <Loader label="Analyzing weather and soil data..." />}

      {!loading && result && (
        <>
          <Card className="bg-gradient-to-r from-primary to-primary-dark p-8 text-center text-white">
            <p className="text-sm uppercase tracking-wide text-primary-light">Expected Yield</p>
            <p className="mt-2 text-4xl font-bold">
              {result.predicted_yield_min} &mdash; {result.predicted_yield_max}{' '}
              <span className="text-lg font-normal">tons/acre</span>
            </p>
            <p className="mt-2 text-primary-light">Confidence: {result.confidence_score}%</p>
          </Card>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Card className="p-5">
              <h3 className="mb-3 flex items-center gap-2 font-semibold text-text-primary">
                <CloudRain className="h-5 w-5 text-primary" />
                Weather Summary Used
              </h3>
              <ul className="flex flex-col gap-2 text-sm text-text-secondary">
                <li className="flex items-center gap-2">
                  <CloudRain className="h-4 w-4" /> Rainfall: {result.weather.rainfall_mm} mm
                </li>
                <li className="flex items-center gap-2">
                  <Thermometer className="h-4 w-4" /> Avg Temperature: {result.weather.avg_temperature_c} °C
                </li>
                <li className="flex items-center gap-2">
                  <Droplets className="h-4 w-4" /> Avg Humidity: {result.weather.avg_humidity_pct}%
                </li>
              </ul>
            </Card>

            <Card className="p-5">
              <h3 className="mb-3 flex items-center gap-2 font-semibold text-text-primary">
                <Sprout className="h-5 w-5 text-primary" />
                Soil Summary Used
              </h3>
              <ul className="flex flex-col gap-2 text-sm text-text-secondary">
                <li>Nitrogen: {soilReport.nitrogen} kg/ha</li>
                <li>Phosphorus: {soilReport.phosphorus} kg/ha</li>
                <li>Potassium: {soilReport.potassium} kg/ha</li>
                <li>pH: {soilReport.ph}</li>
                <li>Soil Fit Score: {result.soil_fit_score}/100</li>
              </ul>
            </Card>
          </div>

          <p className="text-center text-xs text-text-secondary">
            Prediction accuracy improves after first full season of farm data.
          </p>
        </>
      )}
    </div>
  )
}
