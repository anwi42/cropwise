import { Landmark } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import Input from '../../components/common/Input'
import { getErrorMessage, registerBankOfficer } from '../../services/api'

const PHONE_PATTERN = /^[6-9]\d{9}$/

const INITIAL_FORM = {
  name: '',
  phone: '',
  password: '',
  organization: '',
}

export default function BankRegister() {
  const navigate = useNavigate()
  const [form, setForm] = useState(INITIAL_FORM)
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  function updateField(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  function validate() {
    const next = {}
    if (form.name.trim().length < 2) next.name = 'Enter your full name'
    if (!PHONE_PATTERN.test(form.phone)) {
      next.phone = 'Enter a valid 10-digit mobile number starting with 6-9'
    }
    if (form.password.length < 6) next.password = 'Password must be at least 6 characters'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!validate()) return

    setSubmitting(true)
    try {
      await registerBankOfficer({
        name: form.name.trim(),
        phone: form.phone.trim(),
        password: form.password,
        organization: form.organization.trim() || null,
      })
      toast.success('Registration successful! Please login.')
      navigate('/bank/login')
    } catch (error) {
      toast.error(getErrorMessage(error, 'Could not register. Please check your details and try again.'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-white px-4 py-12">
      <Card className="w-full max-w-md p-8">
        <div className="mb-6 flex flex-col items-center text-center">
          <Landmark className="h-8 w-8 text-primary" />
          <h1 className="mt-2 text-2xl font-bold text-text-primary">Bank Officer Registration</h1>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
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
            label="Organization"
            value={form.organization}
            onChange={(e) => updateField('organization', e.target.value)}
          />

          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? 'Registering...' : 'Register'}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-text-secondary">
          Already have an account?{' '}
          <Link to="/bank/login" className="font-medium text-primary hover:underline">
            Login
          </Link>
        </p>
        <p className="mt-2 text-center text-sm text-text-secondary">
          <Link to="/bank" className="hover:underline">
            Back to bank home
          </Link>
        </p>
      </Card>
    </div>
  )
}
