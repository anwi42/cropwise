import { Search } from 'lucide-react'
import { useState } from 'react'
import { toast } from 'react-toastify'
import { getBankFarmerProfile, getErrorMessage, searchBankFarmer } from '../../services/api'
import Button from './Button'
import Input from './Input'

const PHONE_PATTERN = /^[6-9]\d{9}$/

export default function BankFarmerSearchBar({
  onFound,
  onSearchStart,
  officerId,
  placeholder = 'Enter farmer phone number or ID',
}) {
  const [query, setQuery] = useState('')
  const [searching, setSearching] = useState(false)

  async function handleSearch(event) {
    event.preventDefault()
    const trimmed = query.trim()
    if (!trimmed) return

    onSearchStart?.()
    setSearching(true)
    try {
      let farmerId
      if (PHONE_PATTERN.test(trimmed)) {
        const { data } = await searchBankFarmer(trimmed)
        farmerId = data.farmer_id
      } else if (/^\d+$/.test(trimmed)) {
        farmerId = Number(trimmed)
      } else {
        toast.error('Enter a valid 10-digit phone number or a numeric farmer ID')
        return
      }

      const { data: profile } = await getBankFarmerProfile(farmerId, officerId)
      onFound(profile)
    } catch (error) {
      toast.error(getErrorMessage(error, 'Farmer not found'))
      onFound(null)
    } finally {
      setSearching(false)
    }
  }

  return (
    <form onSubmit={handleSearch} className="flex flex-wrap items-start gap-3">
      <div className="min-w-[240px] flex-1">
        <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder={placeholder} />
      </div>
      <Button type="submit" disabled={searching} className="gap-2">
        <Search className="h-4 w-4" />
        {searching ? 'Searching...' : 'Search'}
      </Button>
    </form>
  )
}
