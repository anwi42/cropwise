import { AlertTriangle, CheckCircle2, Download } from 'lucide-react'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { toast } from 'react-toastify'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import Input from '../../components/common/Input'
import Loader from '../../components/common/Loader'
import Select from '../../components/common/Select'
import { CROP_LABELS, CROP_OPTIONS, FARMING_METHOD_OPTIONS } from '../../constants'
import { useAuth } from '../../context/AuthContext'
import { downloadFertilizerPDF, getErrorMessage, getFertilizerPrescription } from '../../services/api'

export default function FertilizerPage() {
  const { farmer, soilReport, cropRecommendation } = useAuth()
  const defaultCrop = cropRecommendation?.recommendations?.[0]?.crop_name || ''
  const [selectedCrop, setSelectedCrop] = useState(defaultCrop)
  const [sowingDate, setSowingDate] = useState('')
  const [farmingMethod, setFarmingMethod] = useState('')
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [prescription, setPrescription] = useState(null)

  const recommendedCropNames = new Set(cropRecommendation?.recommendations?.map((r) => r.crop_name) || [])

  async function handleSubmit(event) {
    event.preventDefault()
    if (!selectedCrop) {
      toast.error('Please select a crop.')
      return
    }
    if (!sowingDate) {
      toast.error('Please select a sowing date.')
      return
    }
    if (!farmingMethod) {
      toast.error('Please select a farming method.')
      return
    }
    setLoading(true)
    try {
      const { data } = await getFertilizerPrescription({
        farmer_id: farmer.farmerId,
        soil_report_id: soilReport.id,
        selected_crop: selectedCrop,
        sowing_date: sowingDate,
        farming_method: farmingMethod,
      })
      setPrescription(data)
      toast.success('Fertilizer prescription generated.')
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not generate a fertilizer prescription. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  async function handleDownload() {
    if (!prescription) return
    setDownloading(true)
    try {
      const { data } = await downloadFertilizerPDF(prescription.fertilizer_prescription_id)
      const blobUrl = window.URL.createObjectURL(new Blob([data], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = `fertilizer_prescription_${prescription.fertilizer_prescription_id}.pdf`
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(blobUrl)
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not download the PDF. Please try again.'))
    } finally {
      setDownloading(false)
    }
  }

  if (!soilReport) {
    return (
      <Card className="p-8 text-center">
        <p className="text-text-secondary">
          You need a soil report before we can prescribe fertilizer.{' '}
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
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <Select
              label="Select Crop"
              placeholder="Select crop"
              options={CROP_OPTIONS.map((opt) => ({
                ...opt,
                label: recommendedCropNames.has(opt.value) ? `${opt.label} (recommended)` : opt.label,
              }))}
              value={selectedCrop}
              onChange={(e) => setSelectedCrop(e.target.value)}
            />
            <Input
              type="date"
              label="Sowing Date"
              value={sowingDate}
              onChange={(e) => setSowingDate(e.target.value)}
            />
            <Select
              label="Farming Method"
              placeholder="Select method"
              options={FARMING_METHOD_OPTIONS}
              value={farmingMethod}
              onChange={(e) => setFarmingMethod(e.target.value)}
            />
          </div>
          <div>
            <Button type="submit" disabled={loading}>
              {loading ? 'Generating...' : 'Generate Prescription'}
            </Button>
          </div>
        </form>
        <p className="mt-3 text-xs text-text-secondary">
          Uses your latest soil report (saved {soilReport.reportDate}) automatically.
        </p>
      </Card>

      {loading && <Loader label="Working out your fertilizer plan..." />}

      {!loading && prescription && (
        <Card className="p-6">
          <h3 className="mb-4 font-semibold text-text-primary">
            Prescription for {CROP_LABELS[prescription.selected_crop] ?? prescription.selected_crop} on{' '}
            {prescription.soil_type_used} soil
          </h3>

          {prescription.items.length === 0 ? (
            <div className="flex items-center gap-2 rounded-lg bg-success/10 p-4 text-success">
              <CheckCircle2 className="h-5 w-5" />
              <span>{prescription.message}</span>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="text-text-secondary">
                    <th className="pb-2 pr-4">Fertilizer</th>
                    <th className="pb-2 pr-4">Chemical Name</th>
                    <th className="pb-2 pr-4">Quantity/Acre</th>
                    <th className="pb-2 pr-4">Timing</th>
                    <th className="pb-2">Organic Alternative</th>
                  </tr>
                </thead>
                <tbody>
                  {prescription.items.map((item, idx) => (
                    <tr key={item.nutrient} className={idx % 2 === 1 ? 'bg-surface' : ''}>
                      <td className="py-2 pr-4 font-medium text-text-primary">{item.fertilizer_name}</td>
                      <td className="py-2 pr-4 text-text-secondary">{item.chemical_name}</td>
                      <td className="py-2 pr-4 text-text-secondary">
                        {item.quantity_per_acre} {item.unit}
                      </td>
                      <td className="py-2 pr-4 text-text-secondary">{item.timing}</td>
                      <td className="py-2 text-text-secondary">{item.organic_alternative}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {prescription.excess_nutrient_warnings.length > 0 && (
            <div className="mt-4 flex flex-col gap-2">
              {prescription.excess_nutrient_warnings.map((warning) => (
                <div key={warning} className="flex items-start gap-2 rounded-lg bg-warning/10 p-3 text-sm text-warning">
                  <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                  <span>{warning}</span>
                </div>
              ))}
            </div>
          )}

          <Button onClick={handleDownload} disabled={downloading} className="mt-6">
            <Download className="h-4 w-4" />
            {downloading ? 'Downloading...' : 'Download PDF'}
          </Button>
        </Card>
      )}
    </div>
  )
}
