import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import { toast } from 'react-toastify'
import Badge from '../../../components/common/Badge'
import BankFarmerSearchBar from '../../../components/common/BankFarmerSearchBar'
import Button from '../../../components/common/Button'
import Card from '../../../components/common/Card'
import Loader from '../../../components/common/Loader'
import { useBankAuth } from '../../../context/BankAuthContext'
import { calculateLoanScore, getBankFarmerProfile, getErrorMessage } from '../../../services/api'

const RISK_TEXT_COLOR = {
  Low: 'text-success',
  Medium: 'text-warning',
  High: 'text-danger',
}

const RISK_BADGE_VARIANT = {
  Low: 'success',
  Medium: 'warning',
  High: 'danger',
}

function formatCurrency(amount) {
  return `₹${Number(amount).toLocaleString('en-IN')}`
}

export default function BankLoanPage() {
  const { officer } = useBankAuth()
  const [searchParams] = useSearchParams()
  const [profile, setProfile] = useState(null)
  const [loadingProfile, setLoadingProfile] = useState(false)
  const [scoring, setScoring] = useState(false)
  const [result, setResult] = useState(null)

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
    setResult(null)
    setLoadingProfile(false)
  }

  async function handleScore() {
    if (!profile) return
    setScoring(true)
    try {
      const { data } = await calculateLoanScore({
        bank_officer_id: officer.officerId,
        farmer_id: profile.farmer_id,
      })
      setResult(data)
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not calculate loan score. Please try again.'))
    } finally {
      setScoring(false)
    }
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
            <Button onClick={handleScore} disabled={scoring}>
              {scoring ? 'Calculating...' : 'Calculate Loan Score'}
            </Button>
          </div>

          {scoring && <Loader label="Calculating loan eligibility..." />}

          {!scoring && result && (
            <div className="flex flex-col gap-6 pt-6">
              <div className="flex flex-col items-center gap-2 text-center">
                <span className={`text-6xl font-bold ${RISK_TEXT_COLOR[result.risk_level]}`}>
                  {result.total_score}
                </span>
                <span className="text-sm text-text-secondary">out of 100</span>
                <Badge variant={RISK_BADGE_VARIANT[result.risk_level]}>{result.risk_level} Risk</Badge>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead>
                    <tr className="text-text-secondary">
                      <th className="pb-2 pr-4">Category</th>
                      <th className="pb-2 pr-4">Points Earned</th>
                      <th className="pb-2 pr-4">Max Points</th>
                      <th className="pb-2">Reason</th>
                    </tr>
                  </thead>
                  <tbody>
                    {result.breakdown.map((row, idx) => (
                      <tr key={row.category} className={idx % 2 === 1 ? 'bg-surface' : ''}>
                        <td className="py-2 pr-4 font-medium text-text-primary">{row.category}</td>
                        <td className="py-2 pr-4 text-text-secondary">{row.points_earned}</td>
                        <td className="py-2 pr-4 text-text-secondary">{row.max_points}</td>
                        <td className="py-2 text-text-secondary">{row.reason}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="rounded-lg bg-primary-light p-4">
                <h3 className="mb-1 text-sm font-semibold text-text-secondary">Recommended Loan Amount</h3>
                <p className="text-xl font-bold text-primary">
                  {formatCurrency(result.recommended_loan_min)} – {formatCurrency(result.recommended_loan_max)}
                </p>
              </div>

              <p className="text-sm text-text-secondary">
                This farmer is assessed as <strong>{result.risk_level.toLowerCase()} risk</strong> based on
                soil health, yield consistency, farm size, crop type and active weather alerts. Scores are
                recalculated fresh at every request and are not cached.
              </p>
            </div>
          )}
        </Card>
      )}
    </div>
  )
}
