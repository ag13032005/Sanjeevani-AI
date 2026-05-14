import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('sanjeevani_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export async function signup(data) {
  const response = await api.post('/signup', data)
  return response.data
}

export async function login(data) {
  const response = await api.post('/login', data)
  return response.data
}

export async function getWeather(lat, lon) {
  const response = await api.get('/weather', { params: { lat, lon } })
  return response.data
}

export async function getAqi(lat, lon) {
  const response = await api.get('/aqi', { params: { lat, lon } })
  return response.data
}

export async function predict(temperature, humidity, aqi, lat, lon) {
  const response = await api.get('/predict', { params: { temperature, humidity, aqi, lat, lon } })
  return response.data
}

export async function getHistory() {
  const response = await api.get('/history')
  return response.data
}

export async function getReport(params) {
  const response = await api.get('/report', { params })
  return response.data
}

export async function submitReport(data) {
  const response = await api.post('/submit-report', data)
  return response.data
}

export async function uploadReport(formData) {
  const response = await api.post('/upload-report', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function getReports() {
  const response = await api.get('/reports')
  return response.data
}

export default api
