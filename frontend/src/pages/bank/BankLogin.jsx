import { Landmark } from 'lucide-react'
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'react-toastify'
import Button from '../../components/common/Button'
import Card from '../../components/common/Card'
import Input from '../../components/common/Input'
import { useBankAuth } from '../../context/BankAuthContext'
import { getErrorMessage, loginBankOfficer } from '../../services/api'

const PHONE_PATTERN = /^[6-9]\d{9}$/

export default function BankLogin() {
  const navigate = useNavigate()
  const { login } = useBankAuth()
  const [phone, setPhone] = useState('')
  const [password, setPassword] = useState('')
  const [errors, setErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  function validate() {
    const next = {}
    if (!PHONE_PATTERN.test(phone)) {
      next.phone = 'Enter a valid 10-digit mobile number starting with 6-9'
    }
    if (!password) next.password = 'Enter your password'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  async function handleSubmit(event) {
    event.preventDefault()
    if (!validate()) return

    setSubmitting(true)
    try {
      const { data } = await loginBankOfficer({ phone, password })
      login(data)
      toast.success(`Welcome back, ${data.name}!`)
      navigate('/bank/dashboard')
    } catch (error) {
      toast.error(getErrorMessage(error, 'Invalid credentials'))
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-primary-light px-4">
      <Card className="w-full max-w-sm p-8">
        <div className="mb-6 flex flex-col items-center text-center">
          <Landmark className="h-8 w-8 text-primary" />
          <h1 className="mt-2 text-2xl font-bold text-text-primary">Bank Officer Login</h1>
          <p className="mt-1 text-sm text-text-secondary">Login to your risk intelligence dashboard</p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <Input
            label="Phone Number"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            error={errors.phone}
            maxLength={10}
            required
          />
          <Input
            label="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            error={errors.password}
            required
          />
          <Button type="submit" disabled={submitting} className="w-full">
            {submitting ? 'Logging in...' : 'Login'}
          </Button>
        </form>

        <p className="mt-4 text-center text-sm text-text-secondary">
          Don&apos;t have an account?{' '}
          <Link to="/bank/register" className="font-medium text-primary hover:underline">
            Register
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
