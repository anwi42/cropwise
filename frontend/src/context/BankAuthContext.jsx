import { createContext, useCallback, useContext, useState } from 'react'

const BankAuthContext = createContext(null)

function readStoredOfficer() {
  const officerId = localStorage.getItem('officer_id')
  if (!officerId) return null
  return {
    officerId: Number(officerId),
    name: localStorage.getItem('officer_name') || '',
    organization: localStorage.getItem('officer_organization') || '',
  }
}

export function BankAuthProvider({ children }) {
  const [officer, setOfficer] = useState(readStoredOfficer)

  const login = useCallback(({ officer_id, name, organization }) => {
    localStorage.setItem('officer_id', String(officer_id))
    localStorage.setItem('officer_name', name || '')
    localStorage.setItem('officer_organization', organization || '')
    setOfficer({ officerId: officer_id, name: name || '', organization: organization || '' })
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('officer_id')
    localStorage.removeItem('officer_name')
    localStorage.removeItem('officer_organization')
    setOfficer(null)
  }, [])

  return (
    <BankAuthContext.Provider
      value={{
        officer,
        isAuthenticated: Boolean(officer),
        login,
        logout,
      }}
    >
      {children}
    </BankAuthContext.Provider>
  )
}

export function useBankAuth() {
  const ctx = useContext(BankAuthContext)
  if (!ctx) throw new Error('useBankAuth must be used within a BankAuthProvider')
  return ctx
}
