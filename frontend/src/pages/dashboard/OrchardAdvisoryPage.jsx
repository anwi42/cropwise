import { AlertTriangle, CloudSun, Droplets, FlaskConical, Scissors, ShieldAlert } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'react-toastify'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import Input from '../../components/common/Input'
import Loader from '../../components/common/Loader'
import Select from '../../components/common/Select'
import { TREE_LABELS, TREE_OPTIONS } from '../../constants'
import { useAuth } from '../../context/AuthContext'
import { getErrorMessage, getOrchardAdvisory } from '../../services/api'

const STAGE_LABELS = {
  establishment: 'Establishment',
  vegetative_growth: 'Vegetative Growth',
  flowering: 'Flowering',
  fruit_development: 'Fruit Development',
  harvest: 'Harvest',
  bearing: 'Year-round Bearing',
}

export default function OrchardAdvisoryPage() {
  const { farmer } = useAuth()
  const [treeType, setTreeType] = useState('')
  const [variety, setVariety] = useState('')
  const [plantingDate, setPlantingDate] = useState('')
  const [treeCount, setTreeCount] = useState('')
  const [areaAcres, setAreaAcres] = useState('')
  const [loading, setLoading] = useState(false)
  const [advisory, setAdvisory] = useState(null)

  async function handleSubmit(event) {
    event.preventDefault()
    if (!treeType) {
      toast.error('Please select a tree type.')
      return
    }
    if (!plantingDate) {
      toast.error('Please select a planting date.')
      return
    }
    setLoading(true)
    try {
      const { data } = await getOrchardAdvisory({
        farmer_id: farmer.farmerId,
        tree_type: treeType,
        variety: variety || undefined,
        planting_date: plantingDate,
        tree_count: treeCount ? Number(treeCount) : undefined,
        area_acres: areaAcres ? Number(areaAcres) : undefined,
      })
      setAdvisory(data)
      toast.success('Orchard advisory generated.')
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not generate orchard advisory. Please try again.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-6">
      <Card className="p-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <Select
              label="Tree Type"
              placeholder="Select tree type"
              options={TREE_OPTIONS}
              value={treeType}
              onChange={(e) => setTreeType(e.target.value)}
            />
            <Input
              label="Variety (optional)"
              placeholder="e.g. Alphonso"
              value={variety}
              onChange={(e) => setVariety(e.target.value)}
            />
            <Input
              type="date"
              label="Planting Date"
              value={plantingDate}
              onChange={(e) => setPlantingDate(e.target.value)}
            />
            <Input
              type="number"
              label="Tree Count (optional)"
              min="1"
              value={treeCount}
              onChange={(e) => setTreeCount(e.target.value)}
            />
            <Input
              type="number"
              label="Area in Acres (optional)"
              min="0.1"
              step="0.1"
              value={areaAcres}
              onChange={(e) => setAreaAcres(e.target.value)}
            />
          </div>
          <div>
            <Button type="submit" disabled={loading}>
              {loading ? 'Generating...' : 'Get Advisory'}
            </Button>
          </div>
        </form>
      </Card>

      {loading && <Loader label="Working out your orchard advisory..." />}

      {!loading && advisory && (
        <div className="flex flex-col gap-6">
          <Card className="p-6">
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="font-semibold text-text-primary">
                  {TREE_LABELS[advisory.tree_type] ?? advisory.tree_type}
                  {advisory.variety ? ` — ${advisory.variety}` : ''}
                </h3>
                <p className="mt-1 text-sm text-text-secondary">{advisory.message}</p>
              </div>
              <span className="inline-flex items-center gap-1 rounded-full bg-primary-light px-3 py-1.5 text-sm font-semibold text-primary">
                {STAGE_LABELS[advisory.growth_stage] ?? advisory.growth_stage}
              </span>
            </div>

            <div className="mt-5 grid grid-cols-1 gap-3 rounded-lg bg-surface p-4 text-sm sm:grid-cols-4">
              <div className="flex items-center gap-2 text-text-secondary">
                <CloudSun className="h-4 w-4 text-primary" />
                <span>
                  Rainfall (14d): <span className="font-medium text-text-primary">{advisory.weather.rainfall_mm} mm</span>
                </span>
              </div>
              <div className="flex items-center gap-2 text-text-secondary">
                <span>
                  Avg Temp: <span className="font-medium text-text-primary">{advisory.weather.avg_temperature_c} °C</span>
                </span>
              </div>
              <div className="text-text-secondary">
                Source: <span className="font-medium text-text-primary">{advisory.weather.source}</span>
              </div>
              <div className="text-text-secondary">
                Age: <span className="font-medium text-text-primary">{advisory.years_since_planting} years</span>
              </div>
            </div>
            {advisory.weather.fallback_used && advisory.weather.warning && (
              <p className="mt-3 text-xs text-warning">{advisory.weather.warning}</p>
            )}
          </Card>

          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <Card className="p-5">
              <div className="mb-2 flex items-center gap-2 font-semibold text-text-primary">
                <Droplets className="h-5 w-5 text-primary" />
                Irrigation
              </div>
              <p className="text-sm text-text-secondary">{advisory.care.irrigation}</p>
            </Card>
            <Card className="p-5">
              <div className="mb-2 flex items-center gap-2 font-semibold text-text-primary">
                <Scissors className="h-5 w-5 text-primary" />
                Pruning
              </div>
              <p className="text-sm text-text-secondary">{advisory.care.pruning}</p>
            </Card>
            <Card className="p-5">
              <div className="mb-2 flex items-center gap-2 font-semibold text-text-primary">
                <FlaskConical className="h-5 w-5 text-primary" />
                Fertigation
              </div>
              <p className="text-sm text-text-secondary">{advisory.care.fertigation}</p>
            </Card>
            <Card className="p-5">
              <div className="mb-2 flex items-center gap-2 font-semibold text-text-primary">
                <ShieldAlert className="h-5 w-5 text-primary" />
                Pest Watch
              </div>
              <p className="text-sm text-text-secondary">{advisory.care.pest_watch}</p>
            </Card>
          </div>

          {advisory.weather_warnings.length > 0 && (
            <Card className="p-6">
              <h3 className="mb-3 font-semibold text-text-primary">Weather Warnings</h3>
              <div className="flex flex-col gap-2">
                {advisory.weather_warnings.map((warning) => (
                  <div key={warning} className="flex items-start gap-2 rounded-lg bg-warning/10 p-3 text-sm text-warning">
                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                    <span>{warning}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}
