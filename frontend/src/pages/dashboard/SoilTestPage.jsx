import { CheckCircle2, Upload, Wheat } from 'lucide-react'
import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import Badge from '../../components/common/Badge'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import Input from '../../components/common/Input'
import Loader from '../../components/common/Loader'
import Select from '../../components/common/Select'
import { CROP_OPTIONS, HEALTH_ZONE_VARIANT, NUTRIENT_LABELS } from '../../constants'
import { useAuth } from '../../context/AuthContext'
import { getErrorMessage, getSoilScore, saveSoilManual, uploadSoilOCR } from '../../services/api'

const FIELD_ORDER = ['nitrogen', 'phosphorus', 'potassium', 'ph', 'organic_carbon']

const NUTRIENT_STATUS_VARIANT = {
  optimal: 'success',
  deficient: 'warning',
  excess: 'danger',
  missing: 'neutral',
}

const EMPTY_MANUAL_FORM = {
  nitrogen: '',
  phosphorus: '',
  potassium: '',
  ph: '',
  organic_carbon: '',
  report_date: '',
  crop_planned: '',
}

function todayISO() {
  return new Date().toISOString().slice(0, 10)
}

export default function SoilTestPage() {
  const navigate = useNavigate()
  const { farmer, setSoilReport, setSoilScore } = useAuth()
  const [tab, setTab] = useState('upload')

  const [file, setFile] = useState(null)
  const [previewUrl, setPreviewUrl] = useState(null)
  const [extracting, setExtracting] = useState(false)
  const [extracted, setExtracted] = useState(null)
  const [ocrValues, setOcrValues] = useState(null)
  const [ocrReportDate, setOcrReportDate] = useState(todayISO)
  const [ocrCrop, setOcrCrop] = useState('')
  const fileInputRef = useRef(null)

  const [manualForm, setManualForm] = useState({ ...EMPTY_MANUAL_FORM, report_date: todayISO() })
  const [errors, setErrors] = useState({})

  const [saving, setSaving] = useState(false)
  const [scoreResult, setScoreResult] = useState(null)

  function resetResult() {
    setScoreResult(null)
  }

  function handleFileChange(event) {
    const selected = event.target.files?.[0]
    if (!selected) return
    setFile(selected)
    setPreviewUrl(URL.createObjectURL(selected))
    setExtracted(null)
    setOcrValues(null)
    resetResult()
  }

  async function handleExtract() {
    if (!file) return
    setExtracting(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      const { data } = await uploadSoilOCR(formData)
      setExtracted(data.extracted_values)
      const values = {}
      FIELD_ORDER.forEach((field) => {
        const value = data.extracted_values[field]?.value
        values[field] = value != null ? String(value) : ''
      })
      setOcrValues(values)
      if (data.needs_manual_review) {
        toast.warning('Some values had low confidence — please review the highlighted rows.')
      } else {
        toast.success('Values extracted successfully.')
      }
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not read the soil report. Please try a clearer image.'))
    } finally {
      setExtracting(false)
    }
  }

  function validateValues(values) {
    const next = {}
    if (values.nitrogen === '' || Number(values.nitrogen) < 0 || Number(values.nitrogen) > 2000) {
      next.nitrogen = 'Enter a value between 0 and 2000'
    }
    if (values.phosphorus === '' || Number(values.phosphorus) < 0 || Number(values.phosphorus) > 2000) {
      next.phosphorus = 'Enter a value between 0 and 2000'
    }
    if (values.potassium === '' || Number(values.potassium) < 0 || Number(values.potassium) > 2000) {
      next.potassium = 'Enter a value between 0 and 2000'
    }
    if (values.ph === '' || Number(values.ph) < 0 || Number(values.ph) > 14) {
      next.ph = 'Enter a value between 0 and 14'
    }
    if (values.organic_carbon === '' || Number(values.organic_carbon) < 0 || Number(values.organic_carbon) > 100) {
      next.organic_carbon = 'Enter a value between 0 and 100'
    }
    return next
  }

  async function saveAndScore({ values, reportDate, cropPlanned, inputMethod }) {
    const soilPayload = {
      farmer_id: farmer.farmerId,
      nitrogen: Number(values.nitrogen),
      phosphorus: Number(values.phosphorus),
      potassium: Number(values.potassium),
      ph: Number(values.ph),
      organic_carbon: Number(values.organic_carbon),
      report_date: reportDate,
      input_method: inputMethod,
    }

    setSaving(true)
    try {
      const { data: manualData } = await saveSoilManual(soilPayload)
      const soilReport = {
        id: manualData.soil_report_id,
        nitrogen: soilPayload.nitrogen,
        phosphorus: soilPayload.phosphorus,
        potassium: soilPayload.potassium,
        ph: soilPayload.ph,
        organicCarbon: soilPayload.organic_carbon,
        reportDate: soilPayload.report_date,
      }
      setSoilReport(soilReport)
      toast.success('Soil report saved.')

      const { data: scoreData } = await getSoilScore({
        farmer_id: farmer.farmerId,
        soil_report_id: manualData.soil_report_id,
        crop_planned: cropPlanned,
      })
      setScoreResult(scoreData)
      setSoilScore({ score: scoreData.health_score, zone: scoreData.health_zone })
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not save your soil report. Please check your values and try again.'))
    } finally {
      setSaving(false)
    }
  }

  function handleManualSubmit(event) {
    event.preventDefault()
    const validation = validateValues(manualForm)
    if (!manualForm.report_date) validation.report_date = 'Select a report date'
    if (!manualForm.crop_planned) validation.crop_planned = 'Select the crop you plan to grow'
    setErrors(validation)
    if (Object.keys(validation).length > 0) return

    saveAndScore({
      values: manualForm,
      reportDate: manualForm.report_date,
      cropPlanned: manualForm.crop_planned,
      inputMethod: 'manual',
    })
  }

  function handleOcrConfirm(event) {
    event.preventDefault()
    const validation = validateValues(ocrValues)
    if (!ocrReportDate) validation.report_date = 'Select a report date'
    if (!ocrCrop) validation.crop_planned = 'Select the crop you plan to grow'
    setErrors(validation)
    if (Object.keys(validation).length > 0) return

    saveAndScore({
      values: ocrValues,
      reportDate: ocrReportDate,
      cropPlanned: ocrCrop,
      inputMethod: 'ocr_corrected',
    })
  }

  function switchTab(next) {
    setTab(next)
    setErrors({})
  }

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-1">
        <div className="flex gap-1 p-1">
          <button
            type="button"
            onClick={() => switchTab('upload')}
            className={`flex-1 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors ${
              tab === 'upload' ? 'bg-primary text-white' : 'text-text-secondary hover:bg-primary-light'
            }`}
          >
            Upload Report
          </button>
          <button
            type="button"
            onClick={() => switchTab('manual')}
            className={`flex-1 rounded-lg px-4 py-2.5 text-sm font-medium transition-colors ${
              tab === 'manual' ? 'bg-primary text-white' : 'text-text-secondary hover:bg-primary-light'
            }`}
          >
            Enter Manually
          </button>
        </div>
      </Card>

      {tab === 'upload' && (
        <Card className="p-6">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/jpeg,image/jpg,image/png,image/webp"
            className="hidden"
            onChange={handleFileChange}
          />
          {!previewUrl ? (
            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="flex w-full flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-primary/40 bg-primary-light/30 py-16 text-center hover:bg-primary-light/60"
            >
              <Upload className="h-10 w-10 text-primary" />
              <span className="font-medium text-text-primary">Click to upload or drag and drop</span>
              <span className="text-sm text-text-secondary">Supports JPG, PNG, WEBP</span>
            </button>
          ) : (
            <div className="flex flex-col items-center gap-4">
              <img src={previewUrl} alt="Soil report preview" className="max-h-64 rounded-lg border border-gray-100" />
              <div className="flex gap-3">
                <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                  Choose a different file
                </Button>
                <Button onClick={handleExtract} disabled={extracting}>
                  {extracting ? 'Extracting...' : 'Extract Values'}
                </Button>
              </div>
            </div>
          )}

          {extracting && <Loader label="Reading your soil report..." />}

          {ocrValues && !extracting && (
            <form onSubmit={handleOcrConfirm} className="mt-8 flex flex-col gap-4">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="text-text-secondary">
                      <th className="pb-2 pr-4">Nutrient</th>
                      <th className="pb-2 pr-4">Extracted Value</th>
                      <th className="pb-2 pr-4">Confidence</th>
                      <th className="pb-2">Edit</th>
                    </tr>
                  </thead>
                  <tbody>
                    {FIELD_ORDER.map((field) => {
                      const info = extracted[field]
                      const lowConfidence = info.needs_manual_correction
                      return (
                        <tr key={field} className={lowConfidence ? 'bg-warning/10' : ''}>
                          <td className="py-2 pr-4 font-medium text-text-primary">{NUTRIENT_LABELS[field]}</td>
                          <td className="py-2 pr-4 text-text-secondary">
                            {info.value != null ? info.value : 'Not found'}
                          </td>
                          <td className="py-2 pr-4 text-text-secondary">{info.confidence}%</td>
                          <td className="py-2">
                            <input
                              type="number"
                              step="0.01"
                              className={`w-28 rounded-lg border px-2 py-1 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 ${
                                errors[field] ? 'border-danger' : 'border-gray-300'
                              }`}
                              value={ocrValues[field]}
                              onChange={(e) => setOcrValues((prev) => ({ ...prev, [field]: e.target.value }))}
                            />
                            {errors[field] && <p className="mt-1 text-xs text-danger">{errors[field]}</p>}
                          </td>
                        </tr>
                      )
                    })}
                  </tbody>
                </table>
              </div>

              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <Input
                  label="Report Date"
                  type="date"
                  value={ocrReportDate}
                  onChange={(e) => setOcrReportDate(e.target.value)}
                  error={errors.report_date}
                  required
                />
                <Select
                  label="Crop You're Planning to Grow"
                  placeholder="Select crop"
                  options={CROP_OPTIONS}
                  value={ocrCrop}
                  onChange={(e) => setOcrCrop(e.target.value)}
                  error={errors.crop_planned}
                />
              </div>

              <Button type="submit" disabled={saving} className="w-full sm:w-auto">
                {saving ? 'Saving...' : 'Confirm and Save'}
              </Button>
            </form>
          )}
        </Card>
      )}

      {tab === 'manual' && (
        <Card className="p-6">
          <form onSubmit={handleManualSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Input
              label="Nitrogen (kg/ha)"
              type="number"
              step="0.01"
              value={manualForm.nitrogen}
              onChange={(e) => setManualForm((prev) => ({ ...prev, nitrogen: e.target.value }))}
              error={errors.nitrogen}
              required
            />
            <Input
              label="Phosphorus (kg/ha)"
              type="number"
              step="0.01"
              value={manualForm.phosphorus}
              onChange={(e) => setManualForm((prev) => ({ ...prev, phosphorus: e.target.value }))}
              error={errors.phosphorus}
              required
            />
            <Input
              label="Potassium (kg/ha)"
              type="number"
              step="0.01"
              value={manualForm.potassium}
              onChange={(e) => setManualForm((prev) => ({ ...prev, potassium: e.target.value }))}
              error={errors.potassium}
              required
            />
            <Input
              label="pH"
              type="number"
              step="0.01"
              min="0"
              max="14"
              value={manualForm.ph}
              onChange={(e) => setManualForm((prev) => ({ ...prev, ph: e.target.value }))}
              error={errors.ph}
              required
            />
            <Input
              label="Organic Carbon (%)"
              type="number"
              step="0.01"
              value={manualForm.organic_carbon}
              onChange={(e) => setManualForm((prev) => ({ ...prev, organic_carbon: e.target.value }))}
              error={errors.organic_carbon}
              required
            />
            <Input
              label="Report Date"
              type="date"
              value={manualForm.report_date}
              onChange={(e) => setManualForm((prev) => ({ ...prev, report_date: e.target.value }))}
              error={errors.report_date}
              required
            />
            <Select
              label="Crop You're Planning to Grow"
              placeholder="Select crop"
              options={CROP_OPTIONS}
              value={manualForm.crop_planned}
              onChange={(e) => setManualForm((prev) => ({ ...prev, crop_planned: e.target.value }))}
              error={errors.crop_planned}
              className="sm:col-span-2"
            />
            <Button type="submit" disabled={saving} className="sm:col-span-2">
              {saving ? 'Saving...' : 'Save Soil Data'}
            </Button>
          </form>
        </Card>
      )}

      {scoreResult && (
        <Card className="p-6">
          <div className="flex flex-col items-center gap-2 text-center">
            <div
              className={`flex h-28 w-28 items-center justify-center rounded-full border-8 text-3xl font-bold ${
                scoreResult.health_zone === 'Green'
                  ? 'border-success text-success'
                  : scoreResult.health_zone === 'Yellow'
                    ? 'border-warning text-warning'
                    : 'border-danger text-danger'
              }`}
            >
              {scoreResult.health_score}
            </div>
            <Badge variant={HEALTH_ZONE_VARIANT[scoreResult.health_zone] ?? 'neutral'}>
              {scoreResult.health_zone} Zone
            </Badge>
            <p className="text-sm text-text-secondary">
              Soil health score for {scoreResult.crop_planned}
            </p>
          </div>

          <div className="mt-6 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="text-text-secondary">
                  <th className="pb-2 pr-4">Nutrient</th>
                  <th className="pb-2 pr-4">Value</th>
                  <th className="pb-2 pr-4">Status</th>
                  <th className="pb-2">Explanation</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(scoreResult.nutrient_details).map(([nutrient, detail], idx) => (
                  <tr key={nutrient} className={idx % 2 === 1 ? 'bg-surface' : ''}>
                    <td className="py-2 pr-4 font-medium text-text-primary">{NUTRIENT_LABELS[nutrient] ?? nutrient}</td>
                    <td className="py-2 pr-4 text-text-secondary">
                      {detail.value != null ? `${detail.value} ${detail.unit}` : '—'}
                    </td>
                    <td className="py-2 pr-4">
                      <Badge variant={NUTRIENT_STATUS_VARIANT[detail.status] ?? 'neutral'}>{detail.status}</Badge>
                    </td>
                    <td className="py-2 text-text-secondary">{detail.explanation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <Button onClick={() => navigate('/dashboard/crops')} className="mt-6 w-full sm:w-auto">
            <Wheat className="h-4 w-4" />
            Get Crop Recommendation
          </Button>
        </Card>
      )}

      {scoreResult && (
        <div className="flex items-center gap-2 text-sm text-success">
          <CheckCircle2 className="h-4 w-4" />
          Soil report saved and scored successfully.
        </div>
      )}
    </div>
  )
}
