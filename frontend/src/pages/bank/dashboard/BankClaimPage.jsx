import { useState } from 'react'
import { toast } from 'react-toastify'
import Badge from '../../../components/common/Badge'
import BankFarmerSearchBar from '../../../components/common/BankFarmerSearchBar'
import Button from '../../../components/common/Button'
import Card from '../../../components/common/Card'
import Input from '../../../components/common/Input'
import Loader from '../../../components/common/Loader'
import Select from '../../../components/common/Select'
import { useBankAuth } from '../../../context/BankAuthContext'
import { getErrorMessage, verifyClaim } from '../../../services/api'

const REASON_OPTIONS = [
  { value: 'flood', label: 'Flood' },
  { value: 'drought', label: 'Drought' },
  { value: 'frost', label: 'Frost' },
  { value: 'pest', label: 'Pest' },
  { value: 'hailstorm', label: 'Hailstorm' },
  { value: 'fire', label: 'Fire' },
]

const RESULT_BADGE_VARIANT = {
  VALIDATED: 'success',
  SUSPICIOUS: 'danger',
  INCONCLUSIVE: 'warning',
}

const RESULT_TEXT_COLOR = {
  VALIDATED: 'text-success',
  SUSPICIOUS: 'text-danger',
  INCONCLUSIVE: 'text-warning',
}

export default function BankClaimPage() {
  const { officer } = useBankAuth()
  const [profile, setProfile] = useState(null)
  const [claimDate, setClaimDate] = useState('')
  const [lossAmount, setLossAmount] = useState('')
  const [reason, setReason] = useState('')
  const [verifying, setVerifying] = useState(false)
  const [result, setResult] = useState(null)

  function handleFound(data) {
    setProfile(data)
    setResult(null)
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!profile) {
      toast.error('Search for a farmer first.')
      return
    }
    if (!claimDate) {
      toast.error('Select a claim date.')
      return
    }
    if (!lossAmount || Number(lossAmount) <= 0) {
      toast.error('Enter a valid claimed loss amount.')
      return
    }
    if (!reason) {
      toast.error('Select a claimed reason.')
      return
    }

    setVerifying(true)
    try {
      const { data } = await verifyClaim({
        bank_officer_id: officer.officerId,
        farmer_id: profile.farmer_id,
        claim_date: claimDate,
        claimed_loss_amount: Number(lossAmount),
        claimed_reason: reason,
      })
      setResult(data)
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not verify this claim. Please try again.'))
    } finally {
      setVerifying(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-6">
        <h3 className="mb-3 text-sm font-semibold text-text-secondary">Farmer</h3>
        <BankFarmerSearchBar
          onFound={handleFound}
          officerId={officer?.officerId}
          placeholder="Enter farmer phone number or ID"
        />
        {profile && (
          <p className="mt-3 text-sm text-text-secondary">
            Selected: <span className="font-medium text-text-primary">{profile.name}</span> (Farmer ID #
            {profile.farmer_id})
          </p>
        )}
      </Card>

      <Card className="p-6">
        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <Input
            type="date"
            label="Claim Date"
            value={claimDate}
            onChange={(e) => setClaimDate(e.target.value)}
            required
          />
          <Input
            type="number"
            label="Claimed Loss Amount (₹)"
            min="0"
            value={lossAmount}
            onChange={(e) => setLossAmount(e.target.value)}
            required
          />
          <Select
            label="Claimed Reason"
            placeholder="Select reason"
            options={REASON_OPTIONS}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
          <div className="sm:col-span-3">
            <Button type="submit" disabled={verifying}>
              {verifying ? 'Verifying...' : 'Verify Claim'}
            </Button>
          </div>
        </form>
      </Card>

      {verifying && <Loader label="Checking weather records..." />}

      {!verifying && result && (
        <Card className="p-6">
          <div className="flex flex-col items-center gap-3 border-b border-gray-100 pb-6 text-center">
            <Badge variant={RESULT_BADGE_VARIANT[result.verification_result]} className="px-4 py-1.5 text-sm">
              {result.verification_result}
            </Badge>
            <p className={`text-lg font-semibold ${RESULT_TEXT_COLOR[result.verification_result]}`}>
              {result.verification_result === 'VALIDATED' && 'Claim supported by weather records'}
              {result.verification_result === 'SUSPICIOUS' && 'Claim not supported by weather records'}
              {result.verification_result === 'INCONCLUSIVE' && 'Requires manual review'}
            </p>
            <p className="max-w-lg text-sm text-text-secondary">{result.explanation}</p>
          </div>

          <div className="grid gap-6 pt-6 sm:grid-cols-2">
            <div>
              <h3 className="mb-2 text-sm font-semibold text-text-secondary">
                Weather Data on Claim Date
              </h3>
              <table className="w-full text-left text-sm">
                <tbody>
                  <tr>
                    <td className="py-1 pr-4 text-text-secondary">Date</td>
                    <td className="py-1 font-medium text-text-primary">{result.weather_data.date || '—'}</td>
                  </tr>
                  <tr>
                    <td className="py-1 pr-4 text-text-secondary">Rainfall</td>
                    <td className="py-1 font-medium text-text-primary">
                      {result.weather_data.rainfall_mm != null ? `${result.weather_data.rainfall_mm} mm` : 'Not available'}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-1 pr-4 text-text-secondary">Min Temperature</td>
                    <td className="py-1 font-medium text-text-primary">
                      {result.weather_data.temp_min_c != null ? `${result.weather_data.temp_min_c} °C` : 'Not available'}
                    </td>
                  </tr>
                  <tr>
                    <td className="py-1 pr-4 text-text-secondary">Max Temperature</td>
                    <td className="py-1 font-medium text-text-primary">
                      {result.weather_data.temp_max_c != null ? `${result.weather_data.temp_max_c} °C` : 'Not available'}
                    </td>
                  </tr>
                </tbody>
              </table>
              {result.weather_data.warning && (
                <p className="mt-2 text-xs text-danger">{result.weather_data.warning}</p>
              )}
            </div>

            <div>
              <h3 className="mb-2 text-sm font-semibold text-text-secondary">
                Yield Prediction at Time of Claim
              </h3>
              {result.yield_data ? (
                <div className="rounded-lg bg-surface p-4 text-sm">
                  <p className="font-medium text-text-primary">
                    {result.yield_data.crop_type} ({result.yield_data.crop_variety})
                  </p>
                  <p className="mt-1 text-text-secondary">Sown: {result.yield_data.sowing_date}</p>
                  <p className="text-text-secondary">
                    Predicted yield: {result.yield_data.predicted_yield_min}–
                    {result.yield_data.predicted_yield_max} tons/acre
                  </p>
                </div>
              ) : (
                <p className="text-sm text-text-secondary">No yield prediction on record for this farmer</p>
              )}
            </div>
          </div>
        </Card>
      )}
    </div>
  )
}
