import { createContext, useCallback, useContext, useState } from 'react'

const AuthContext = createContext(null)

function readStoredFarmer() {
  const farmerId = localStorage.getItem('farmer_id')
  if (!farmerId) return null
  return {
    farmerId: Number(farmerId),
    name: localStorage.getItem('farmer_name') || '',
    preferredLanguage: localStorage.getItem('farmer_language') || 'english',
  }
}

function readStoredSoilReport() {
  const raw = localStorage.getItem('soil_report')
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [farmer, setFarmer] = useState(readStoredFarmer)
  const [soilReport, setSoilReportState] = useState(readStoredSoilReport)
  const [soilScore, setSoilScore] = useState(null)
  const [cropRecommendation, setCropRecommendation] = useState(null)
  const [yieldPrediction, setYieldPrediction] = useState(null)
  const [alerts, setAlerts] = useState(null)
  const [alertsCheckedAt, setAlertsCheckedAt] = useState(null)

  const login = useCallback(({ farmer_id, name, preferred_language }) => {
    localStorage.setItem('farmer_id', String(farmer_id))
    localStorage.setItem('farmer_name', name || '')
    localStorage.setItem('farmer_language', preferred_language || 'english')
    setFarmer({ farmerId: farmer_id, name: name || '', preferredLanguage: preferred_language || 'english' })
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('farmer_id')
    localStorage.removeItem('farmer_name')
    localStorage.removeItem('farmer_language')
    localStorage.removeItem('soil_report')
    setFarmer(null)
    setSoilReportState(null)
    setSoilScore(null)
    setCropRecommendation(null)
    setYieldPrediction(null)
    setAlerts(null)
    setAlertsCheckedAt(null)
  }, [])

  const setSoilReport = useCallback((report) => {
    setSoilReportState(report)
    setSoilScore(null)
    if (report) {
      localStorage.setItem('soil_report', JSON.stringify(report))
    } else {
      localStorage.removeItem('soil_report')
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{
        farmer,
        isAuthenticated: Boolean(farmer),
        login,
        logout,
        soilReport,
        setSoilReport,
        soilScore,
        setSoilScore,
        cropRecommendation,
        setCropRecommendation,
        yieldPrediction,
        setYieldPrediction,
        alerts,
        setAlerts,
        alertsCheckedAt,
        setAlertsCheckedAt,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within an AuthProvider')
  return ctx
}
