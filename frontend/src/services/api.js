import axios from 'axios'

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
})

export const registerFarmer = (data) => api.post('/api/register', data)
export const loginFarmer = (data) => api.post('/api/login', data)

export const registerBankOfficer = (data) => api.post('/api/bank/register', data)
export const loginBankOfficer = (data) => api.post('/api/bank/login', data)

export const searchBankFarmer = (phone) => api.get('/api/bank/farmer/search', { params: { phone } })
export const getBankFarmerProfile = (farmerId, officerId) =>
  api.get(`/api/bank/farmer/${farmerId}`, { params: officerId ? { bank_officer_id: officerId } : {} })

export const generateCertificate = (data) => api.post('/api/bank/certificate/generate', data)
export const downloadCertificatePDF = (certificateId) =>
  api.get(`/api/bank/certificate/${certificateId}/pdf`, { responseType: 'blob' })
export const verifyCertificate = (code) => api.get(`/api/bank/certificate/verify/${code}`)

export const calculateLoanScore = (data) => api.post('/api/bank/loan/score', data)

export const verifyClaim = (data) => api.post('/api/bank/claim/verify', data)

export const getBankPortfolio = (officerId) => api.get(`/api/bank/portfolio/${officerId}`)
export const getBankOverview = (officerId) => api.get(`/api/bank/overview/${officerId}`)

export const uploadSoilOCR = (formData) =>
  api.post('/api/soil/ocr', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
export const saveSoilManual = (data) => api.post('/api/soil/manual', data)
export const getSoilScore = (data) => api.post('/api/soil/score', data)

export const getCropRecommendation = (data) => api.post('/api/crop/recommend', data)

export const getFertilizerPrescription = (data) => api.post('/api/soil/fertilizer', data)
export const downloadFertilizerPDF = (prescriptionId) =>
  api.get(`/api/soil/fertilizer/${prescriptionId}/pdf`, { responseType: 'blob' })

export const getOrchardAdvisory = (data) => api.post('/api/orchard/advisory', data)

export const predictYield = (data) => api.post('/api/yield/predict', data)

export const runWeatherCheck = () => api.post('/api/alerts/run-check')
export const getAlerts = (farmerId) => api.get(`/api/alerts/${farmerId}`)

// Backend errors arrive as either a plain string detail or a
// {success, message} object (see auth.py) - never show either raw form
// to the farmer, always reduce to one friendly line.
export function getErrorMessage(error, fallback = 'Something went wrong. Please try again.') {
  const detail = error?.response?.data?.detail
  if (typeof detail === 'string') return detail
  if (detail && typeof detail === 'object' && typeof detail.message === 'string') {
    return detail.message
  }
  if (error?.message === 'Network Error') {
    return 'Could not reach the server. Please check your connection and try again.'
  }
  return fallback
}

export default api
