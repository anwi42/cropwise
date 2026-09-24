import { CheckCircle2, Landmark, XCircle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import Card from '../../components/common/Card'
import Loader from '../../components/common/Loader'
import { verifyCertificate } from '../../services/api'

export default function CertificateVerify() {
  const { code } = useParams()
  const [certificate, setCertificate] = useState(null)
  const [notFound, setNotFound] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setNotFound(false)
    verifyCertificate(code)
      .then(({ data }) => {
        if (!cancelled) setCertificate(data)
      })
      .catch(() => {
        if (!cancelled) setNotFound(true)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [code])

  return (
    <div className="flex min-h-screen flex-col items-center bg-surface px-4 py-16">
      <div className="mb-8 flex items-center gap-2 text-lg font-bold text-text-primary">
        <Landmark className="h-6 w-6 text-primary" />
        CropWise <span className="font-normal text-text-secondary">for Banks</span>
      </div>

      <Card className="w-full max-w-lg p-8 text-center">
        {loading && <Loader label="Verifying certificate..." />}

        {!loading && notFound && (
          <div className="flex flex-col items-center gap-3">
            <XCircle className="h-16 w-16 text-danger" />
            <h1 className="text-2xl font-bold text-danger">DOCUMENT NOT FOUND</h1>
            <p className="text-sm text-text-secondary">
              No certificate matches this verification code. It may be invalid or the document may be
              fraudulent.
            </p>
          </div>
        )}

        {!loading && certificate && (
          <div className="flex flex-col items-center gap-3">
            <CheckCircle2 className="h-16 w-16 text-success" />
            <h1 className="text-2xl font-bold text-success">AUTHENTIC DOCUMENT</h1>
            <p className="text-sm text-text-secondary">
              This yield certificate was issued by CropWise and has not been altered.
            </p>

            <div className="mt-4 w-full rounded-lg bg-surface p-4 text-left text-sm">
              <dl className="space-y-2">
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Certificate ID</dt>
                  <dd className="font-medium text-text-primary">#{certificate.certificate_id}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Farmer</dt>
                  <dd className="font-medium text-text-primary">{certificate.farmer_name}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Location</dt>
                  <dd className="font-medium text-text-primary">
                    {[certificate.village, certificate.district, certificate.state]
                      .filter(Boolean)
                      .join(', ') || '—'}
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Crop</dt>
                  <dd className="font-medium capitalize text-text-primary">{certificate.crop_type}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Predicted Yield</dt>
                  <dd className="font-medium text-text-primary">
                    {certificate.predicted_yield_min}–{certificate.predicted_yield_max} tons/acre
                  </dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Confidence</dt>
                  <dd className="font-medium text-text-primary">{certificate.confidence_score}%</dd>
                </div>
                {certificate.soil_health_score != null && (
                  <div className="flex justify-between">
                    <dt className="text-text-secondary">Soil Health Score</dt>
                    <dd className="font-medium text-text-primary">{certificate.soil_health_score}</dd>
                  </div>
                )}
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Issued By</dt>
                  <dd className="font-medium text-text-primary">{certificate.bank_officer_name}</dd>
                </div>
                <div className="flex justify-between">
                  <dt className="text-text-secondary">Generated</dt>
                  <dd className="font-medium text-text-primary">
                    {new Date(certificate.generated_at).toLocaleString()}
                  </dd>
                </div>
              </dl>
              <p className="mt-3 break-all text-xs text-text-secondary">
                Document Hash: {certificate.document_hash}
              </p>
            </div>
          </div>
        )}
      </Card>
    </div>
  )
}
