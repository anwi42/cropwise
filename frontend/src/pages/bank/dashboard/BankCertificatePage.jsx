import { Copy, Download, FileCheck2 } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'react-toastify'
import Badge from '../../../components/common/Badge'
import BankFarmerSearchBar from '../../../components/common/BankFarmerSearchBar'
import Button from '../../../components/common/Button'
import Card from '../../../components/common/Card'
import Loader from '../../../components/common/Loader'
import { HEALTH_ZONE_VARIANT } from '../../../constants'
import { useBankAuth } from '../../../context/BankAuthContext'
import {
  downloadCertificatePDF,
  generateCertificate,
  getBankFarmerProfile,
  getErrorMessage,
} from '../../../services/api'

export default function BankCertificatePage() {
  const { officer } = useBankAuth()
  const [searchParams] = useSearchParams()
  const [profile, setProfile] = useState(null)
  const [loadingProfile, setLoadingProfile] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [certificate, setCertificate] = useState(null)

  useEffect(() => {
    const farmerId = searchParams.get('farmer_id')
    if (!farmerId) return

    setLoadingProfile(true)
    getBankFarmerProfile(farmerId, officer?.officerId)
      .then(({ data }) => setProfile(data))
      .catch((error) => toast.error(getErrorMessage(error, 'Farmer not found')))
      .finally(() => setLoadingProfile(false))
  }, [searchParams, officer])

  function handleFound(data) {
    setProfile(data)
    setCertificate(null)
    setLoadingProfile(false)
  }

  async function handleGenerate() {
    if (!profile) return
    setGenerating(true)
    try {
      const { data } = await generateCertificate({
        bank_officer_id: officer.officerId,
        farmer_id: profile.farmer_id,
      })
      setCertificate(data)
      toast.success('Certificate generated.')
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not generate certificate. Please try again.'))
    } finally {
      setGenerating(false)
    }
  }

  async function handleDownload() {
    if (!certificate) return
    setDownloading(true)
    try {
      const { data } = await downloadCertificatePDF(certificate.certificate_id)
      const blobUrl = window.URL.createObjectURL(new Blob([data], { type: 'application/pdf' }))
      const link = document.createElement('a')
      link.href = blobUrl
      link.download = `yield_certificate_${certificate.certificate_id}.pdf`
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

  function handleCopyLink() {
    if (!certificate) return
    const url = `${window.location.origin}/bank/verify/${certificate.verification_code}`
    navigator.clipboard
      .writeText(url)
      .then(() => toast.success('Verification link copied.'))
      .catch(() => toast.error('Could not copy link.'))
  }

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-6">
        <BankFarmerSearchBar
          onSearchStart={() => setLoadingProfile(true)}
          onFound={handleFound}
          officerId={officer?.officerId}
        />
      </Card>

      {loadingProfile && !profile && <Loader label="Looking up farmer..." />}

      {profile && (
        <Card className="p-6">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-gray-100 pb-4">
            <div>
              <h2 className="text-lg font-bold text-text-primary">{profile.name}</h2>
              <p className="text-sm text-text-secondary">
                {[profile.village, profile.district, profile.state].filter(Boolean).join(', ')}
              </p>
            </div>
            {!certificate && (
              <Button onClick={handleGenerate} disabled={generating || !profile.latest_yield_prediction}>
                {generating ? 'Generating...' : 'Generate Certificate'}
              </Button>
            )}
          </div>

          {!profile.latest_yield_prediction && (
            <p className="mt-4 text-sm text-danger">
              This farmer has no yield prediction on record yet. A yield prediction is required before a
              certificate can be generated.
            </p>
          )}

          <div className="grid gap-4 py-4 sm:grid-cols-2">
            <div className="rounded-lg bg-surface p-4 text-sm">
              <h3 className="mb-2 font-semibold text-text-secondary">Farm Details</h3>
              <p>Farm Size: {profile.farm_size != null ? `${profile.farm_size} acres` : 'Not on file'}</p>
              <p className="capitalize">Soil Type: {profile.soil_type || 'Not on file'}</p>
            </div>
            <div className="rounded-lg bg-surface p-4 text-sm">
              <h3 className="mb-2 font-semibold text-text-secondary">Soil Health</h3>
              {profile.latest_soil_report?.health_score != null ? (
                <div className="flex items-center gap-2">
                  <span className="text-xl font-bold text-text-primary">
                    {profile.latest_soil_report.health_score}
                  </span>
                  <Badge variant={HEALTH_ZONE_VARIANT[profile.latest_soil_report.health_zone] || 'neutral'}>
                    {profile.latest_soil_report.health_zone} Zone
                  </Badge>
                </div>
              ) : (
                <p>Not scored</p>
              )}
            </div>
            {profile.latest_yield_prediction && (
              <div className="rounded-lg bg-surface p-4 text-sm sm:col-span-2">
                <h3 className="mb-2 font-semibold text-text-secondary">Yield Prediction</h3>
                <p>
                  {profile.latest_yield_prediction.crop_type} ({profile.latest_yield_prediction.crop_variety}):{' '}
                  {profile.latest_yield_prediction.predicted_yield_min}–
                  {profile.latest_yield_prediction.predicted_yield_max} tons/acre, confidence{' '}
                  {profile.latest_yield_prediction.confidence_score}%
                </p>
              </div>
            )}
          </div>

          {certificate && (
            <div className="mt-4 rounded-lg border border-primary-light bg-primary-light/40 p-4">
              <div className="mb-3 flex items-center gap-2 text-primary">
                <FileCheck2 className="h-5 w-5" />
                <span className="font-semibold">Certificate #{certificate.certificate_id} generated</span>
              </div>
              <p className="break-all text-xs text-text-secondary">
                Document Hash: {certificate.document_hash}
              </p>
              <p className="break-all text-xs text-text-secondary">
                Verification Code: {certificate.verification_code}
              </p>
              <div className="mt-4 flex flex-wrap gap-3">
                <Button onClick={handleDownload} disabled={downloading} className="gap-2">
                  <Download className="h-4 w-4" />
                  {downloading ? 'Downloading...' : 'Download PDF'}
                </Button>
                <Button variant="outline" onClick={handleCopyLink} className="gap-2">
                  <Copy className="h-4 w-4" />
                  Copy Verification Link
                </Button>
              </div>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
