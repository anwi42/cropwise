import { Leaf } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import Button from '../components/common/Button'
import Card from '../components/common/Card'
import Input from '../components/common/Input'
import Select from '../components/common/Select'
import { getErrorMessage, registerFarmer } from '../services/api'

const INDIAN_STATES = [
  'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat',
  'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh',
  'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab',
  'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh',
  'Uttarakhand', 'West Bengal', 'Andaman and Nicobar Islands', 'Chandigarh',
  'Dadra and Nagar Haveli and Daman and Diu', 'Delhi', 'Jammu and Kashmir', 'Ladakh',
  'Lakshadweep', 'Puducherry',
].map((state) => ({ value: state, label: state }))

// Values must match app.yield_config.SOIL_TYPE_ENCODING on the backend -
// these are what the fertilizer/yield lookups key farms.soil_type against.
const SOIL_TYPES = [
  { value: 'alluvial', label: 'Alluvial' },
  { value: 'black', label: 'Black Cotton' },
  { value: 'clayey', label: 'Clayey' },
  { value: 'loamy', label: 'Loamy' },
  { value: 'red', label: 'Red Laterite' },
]

const WATER_SOURCES = ['Borewell', 'Canal', 'Rainwater', 'Drip Irrigation'].map((source) => ({
  value: source,
  label: source,
}))

const CROPS = ['Wheat', 'Rice', 'Tomato', 'Onion', 'Soybean', 'Maize', 'Cotton', 'Sugarcane']

const LANGUAGES = [
  'English', 'Hindi', 'Marathi', 'Telugu', 'Tamil', 'Punjabi', 'Gujarati', 'Kannada',
].map((lang) => ({ value: lang.toLowerCase(), label: lang }))

const PHONE_PATTERN = /^[6-9]\d{9}$/

const INITIAL_FORM = {
  name: '',
  phone: '',
  password: '',
  village: '',
  taluka: '',
  district: '',
  state: '',
  farm_size: '',
  soil_type: '',
  water_source: '',
  preferred_language: 'english',
}

export default function Register() {
  const navigate = useNavigate()
  const [form, setForm] = useState(INITIAL_FORM)
  const [cropsGrownBefore, setCropsGrownBefore] = useState([])
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function toggleCrop(crop) {
    setCropsGrownBefore((prev) =>
      prev.includes(crop) ? prev.filter((c) => c !== crop) : [...prev, crop]
    )
  }

  function validate() {
    const next = {}
    if (form.name.trim().length < 2) next.name = 'Enter your full name'
    if (!PHONE_PATTERN.test(form.phone)) {
      next.phone = 'Enter a valid 10-digit mobile number starting with 6-9'
    }
    if (form.password.length < 6) next.password = 'Password must be at least 6 characters'
    if (form.farm_size && Number(form.farm_size) <= 0) {
      next.farm_size = 'Farm size must be greater than 0'
    }
    setErrors(next)
    return Object.keys(next).length === 0
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!validate()) return

    setSubmitting(true)
    try {
      await registerFarmer({
        name: form.name.trim(),
        phone: form.phone.trim(),
        password: form.password,
        preferred_language: form.preferred_language,
        village: form.village.trim() || null,
        taluka: form.taluka.trim() || null,
        district: form.district.trim() || null,
        state: form.state || null,
        farm_size: form.farm_size ? Number(form.farm_size) : null,
        soil_type: form.soil_type || null,
        water_source: form.water_source || null,
        crops_grown_before: cropsGrownBefore.map((crop) => crop.toLowerCase()),
      })
      toast.success('Registration successful! Please login.')
      navigate('/login')
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not register. Please check your details and try again.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-white px-4 py-12">
      <Card className="w-full max-w-2xl p-8">
        <div className="mb-6 flex flex-col items-center text-center">
          <Leaf className="h-8 w-8 text-primary" />
          <h1 className="mt-2 text-2xl font-bold text-text-primary">Create Your Account</h1>
        </div>

        <form onSubmit={handleSubmit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Input
            label="Full Name"
            value={form.name}
            onChange={(e) => updateField('name', e.target.value)}
            error={errors.name}
            required
          />
          <Input
            label="Phone Number"
            value={form.phone}
            onChange={(e) => updateField('phone', e.target.value)}
            error={errors.phone}
            maxLength={10}
            required
          />
          <Input
            label="Password"
            type="password"
            value={form.password}
            onChange={(e) => updateField('password', e.target.value)}
            error={errors.password}
            required
          />
          <Input
            label="Farm Size (acres)"
            type="number"
            min="0"
            step="0.1"
            value={form.farm_size}
            onChange={(e) => updateField('farm_size', e.target.value)}
            error={errors.farm_size}
          />
          <Input
            label="Village"
            value={form.village}
            onChange={(e) => updateField('village', e.target.value)}
          />
          <Input
            label="Taluka"
            value={form.taluka}
            onChange={(e) => updateField('taluka', e.target.value)}
          />
          <Input
            label="District"
            value={form.district}
            onChange={(e) => updateField('district', e.target.value)}
          />
          <Select
            label="State"
            placeholder="Select state"
            options={INDIAN_STATES}
            value={form.state}
            onChange={(e) => updateField('state', e.target.value)}
          />
          <Select
            label="Soil Type"
            placeholder="Select soil type"
            options={SOIL_TYPES}
            value={form.soil_type}
            onChange={(e) => updateField('soil_type', e.target.value)}
          />
          <Select
            label="Water Source"
            placeholder="Select water source"
            options={WATER_SOURCES}
            value={form.water_source}
            onChange={(e) => updateField('water_source', e.target.value)}
          />
          <Select
            label="Preferred Language"
            options={LANGUAGES}
            value={form.preferred_language}
            onChange={(e) => updateField('preferred_language', e.target.value)}
            className="sm:col-span-2"
          />

          <div className="sm:col-span-2">
            <span className="text-sm font-medium text-text-secondary">Crops Grown Before</span>
            <div className="mt-2 grid grid-cols-2 gap-2 sm:grid-cols-4">
              {CROPS.map((crop) => (
                <label key={crop} className="flex items-center gap-2 text-sm text-text-primary">
                  <input
                    type="checkbox"
                    className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
                    checked={cropsGrownBefore.includes(crop)}
                    onChange={() => toggleCrop(crop)}
                  />
                  {crop}
                </label>
              ))}
            </div>
          </div>

          <Button type="submit" disabled={submitting} className="w-full sm:col-span-2">
            {submitting ? 'Registering...' : 'Register'}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-text-secondary">
          Already have an account?{' '}
          <Link to="/login" className="font-medium text-primary hover:underline">
            Login
          </Link>
        </p>
      </Card>
    </div>
  )
}
