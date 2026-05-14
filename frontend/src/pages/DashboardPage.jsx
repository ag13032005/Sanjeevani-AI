import { useEffect, useMemo, useState } from 'react'
import { getAqi, getHistory, getReport, getWeather, predict } from '../services/api'
import MetricCard from '../components/MetricCard'
import PredictionChart from '../components/PredictionChart'
import { useAuth } from '../context/useAuth'
import ReportGrid from '../components/report/ReportGrid'
import { Link } from 'react-router-dom'
import { getReports } from '../services/api'

const riskCopy = {
  Low: { tone: 'Low', accent: 'from-lime to-aqua', text: 'Current conditions look stable, but continued monitoring is still useful.' },
  Medium: { tone: 'Medium', accent: 'from-amber-400 to-ember', text: 'Risk is rising. Keep an eye on humidity and public health alerts.' },
  High: { tone: 'High', accent: 'from-rose-500 to-ember', text: 'High risk detected. Trigger mitigation and public health messaging immediately.' },
}

const defaultLatitude = 19.076
const defaultLongitude = 72.8777

export default function DashboardPage() {
  const { user } = useAuth()
  const [lat, setLat] = useState(defaultLatitude)
  const [lon, setLon] = useState(defaultLongitude)
  const [weather, setWeather] = useState(null)
  const [aqi, setAqi] = useState(null)
  const [prediction, setPrediction] = useState(null)
  const [history, setHistory] = useState([])
  const [reports, setReports] = useState([])
  const [showHistory, setShowHistory] = useState(false)
  const [report, setReport] = useState(null)
  const [reportLoading, setReportLoading] = useState(false)
  const [reportError, setReportError] = useState('')
  const [patientForm, setPatientForm] = useState({
    name: user?.name || 'Patient',
    id: 'PT-001',
    heart_rate: 82,
    bp_systolic: 128,
    bp_diastolic: 82,
    temperature: 36.8,
    spo2: 98,
    ecg: 'Normal Sinus Rhythm',
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const risk = prediction?.risk_level || 'Low'
  const riskData = riskCopy[risk] || riskCopy.Low

  const loadHistory = async () => {
    try {
      const data = await getHistory()
      setHistory(data)
    } catch {
      setHistory([])
    }
  }

  const loadReports = async () => {
    try {
      const data = await getReports()
      setReports(data)
    } catch {
      setReports([])
    }
  }

  useEffect(() => {
    loadHistory()
    loadReports()
  }, [])

  useEffect(() => {
    setPatientForm((current) => ({ ...current, name: user?.name || current.name }))
  }, [user?.name])

  const handleLocate = () => {
    setError('')

    if (!navigator.geolocation) {
      setLat(defaultLatitude)
      setLon(defaultLongitude)
      return
    }

    const options = {
      enableHighAccuracy: false,
      timeout: 10000,
      maximumAge: 600000,
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLat(position.coords.latitude)
        setLon(position.coords.longitude)
        setError('')
      },
      () => {
        setLat(defaultLatitude)
        setLon(defaultLongitude)
      },
      options,
    )
  }

  const handleAnalyze = async () => {
    setLoading(true)
    setError('')
    try {
      const [weatherData, aqiData] = await Promise.all([getWeather(lat, lon), getAqi(lat, lon)])
      setWeather(weatherData)
      setAqi(aqiData)
      const predictionData = await predict(weatherData.temperature, weatherData.humidity, aqiData.aqi, lat, lon)
      setPrediction(predictionData)
      await loadHistory()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to run prediction')
    } finally {
      setLoading(false)
    }
  }

  const handleViewHistory = async () => {
    await loadHistory()
    setShowHistory((current) => !current)
  }

  const handleGenerateReport = async () => {
    setReportLoading(true)
    setReportError('')
    try {
      const data = await getReport({
        patient_name: patientForm.name,
        patient_id: patientForm.id,
        heart_rate: patientForm.heart_rate,
        bp_systolic: patientForm.bp_systolic,
        bp_diastolic: patientForm.bp_diastolic,
        temperature: patientForm.temperature,
        spo2: patientForm.spo2,
        ecg: patientForm.ecg,
      })
      setReport(data)
      await loadReports()
    } catch (err) {
      setReportError(err?.response?.data?.detail || 'Unable to generate report')
    } finally {
      setReportLoading(false)
    }
  }

  const metrics = useMemo(() => {
    return [
      { label: 'Risk level', value: prediction?.risk || prediction?.risk_level || '—', helper: prediction ? riskData.text : 'Run the model to generate an outbreak risk classification.', accent: riskData.accent },
      { label: 'Disease Prediction', value: prediction ? `${prediction.disease} (${riskData.tone} Probability)` : '—', helper: prediction ? prediction.explanation : 'The backend now maps weather and AQI to a probable disease type.', accent: 'from-cyan-400 to-aqua' },
      { label: 'Temperature', value: weather ? `${weather.temperature.toFixed(1)}°C` : '—', helper: weather ? `Source: ${weather.source}` : 'Fetched from OpenWeather or fallback mock data.', accent: 'from-aqua to-ocean' },
      { label: 'Humidity', value: weather ? `${weather.humidity.toFixed(0)}%` : '—', helper: 'Humidity is a core signal for many mosquito-borne outbreaks.', accent: 'from-lime to-aqua' },
      { label: 'AQI', value: aqi ? `${aqi.aqi}` : '—', helper: aqi ? `${aqi.category} air quality` : 'Air pollution is fetched in real time for the selected location.', accent: 'from-ember to-ocean' },
    ]
  }, [prediction, weather, aqi, riskData])

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-8 rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 p-5 shadow-lg lg:p-8">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
          <div>
          <p className="text-sm uppercase tracking-[0.35em] text-aqua">Dashboard</p>
          <h1 className="mt-4 font-display text-4xl font-bold text-white text-balance">Good to see you, {user?.name || 'Researcher'}.</h1>
          <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-300">
            Pull real-time weather and AQI for a location, run the outbreak risk model, and preserve the prediction history per user.
          </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <button onClick={handleLocate} className="rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">Use my location</button>
            <button onClick={handleAnalyze} disabled={loading} className="rounded-full bg-gradient-to-r from-aqua to-ocean px-5 py-3 text-sm font-semibold text-white shadow-glow transition hover:brightness-110 disabled:opacity-70">
              {loading ? 'Analyzing...' : 'Run prediction'}
            </button>
            <button onClick={handleViewHistory} className="rounded-full border border-white/15 px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/10">
              {showHistory ? 'Hide History' : 'View History'}
            </button>
            <Link to="/submit-report" className="rounded-full border border-aqua/40 bg-aqua/10 px-5 py-3 text-sm font-semibold text-aqua transition hover:bg-aqua/20">
              Submit Medical Report
            </Link>
          </div>
        </div>

        <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <label className="block">
              <span className="mb-2 block text-sm text-slate-400">Latitude</span>
              <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={lat} onChange={(e) => setLat(Number(e.target.value))} />
            </label>
            <label className="block">
              <span className="mb-2 block text-sm text-slate-400">Longitude</span>
              <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={lon} onChange={(e) => setLon(Number(e.target.value))} />
            </label>
          </div>
          {error ? <p className="mt-5 rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</p> : null}
        </div>

      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-5">
        {metrics.map((metric) => (
          <MetricCard key={metric.label} {...metric} />
        ))}
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <PredictionChart history={history} />
        <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 p-5 shadow-lg">
          <p className="text-sm uppercase tracking-[0.35em] text-slate-400">Recommendation</p>
          <h2 className={`mt-4 font-display text-3xl font-bold text-white`}>{riskData.tone} risk</h2>
          <p className="mt-4 text-slate-300">{prediction?.recommendation || 'Execute the model to receive a contextual recommendation.'}</p>
          <div className={`mt-6 rounded-xl border border-red-400 bg-red-500/20 p-5 text-white`}>
            <p className="text-sm font-semibold uppercase tracking-[0.28em] text-slate-950/70">Alert</p>
            <p className="mt-3 text-lg font-semibold">{prediction ? prediction.recommendation : 'No active prediction yet.'}</p>
          </div>
        </div>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="card-surface rounded-[2rem] p-5 shadow-glow">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.26em] text-slate-400">Live data</p>
              <h3 className="font-display text-xl text-white">Weather and AQI snapshot</h3>
            </div>
            <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-300">Last 50 records</span>
          </div>
          <div className="space-y-4 text-sm text-slate-300">
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-slate-400">Weather</p>
              <p className="mt-2 text-base text-white">{weather ? `${weather.temperature.toFixed(1)}°C, ${weather.humidity.toFixed(0)}% humidity, ${weather.description}` : 'Run prediction to load data.'}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-slate-400">AQI</p>
              <p className="mt-2 text-base text-white">{aqi ? `${aqi.aqi} (${aqi.category})` : 'Run prediction to load AQI.'}</p>
            </div>
            <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
              <p className="text-slate-400">Prediction count</p>
              <p className="mt-2 text-base text-white">{history.length} saved predictions for this account</p>
            </div>
          </div>
        </div>

        <div className="card-surface rounded-[2rem] p-5 shadow-glow">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.26em] text-slate-400">Patient Reports</p>
              <h3 className="font-display text-xl text-white">Recent reports</h3>
            </div>
            <Link to="/submit-report" className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-200 transition hover:bg-white/15">Open form</Link>
          </div>
          <div className="space-y-3">
            {reports.length ? reports.slice(0, 5).map((item) => (
              <div key={item.id} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <p className="font-semibold text-white">{item.patient_name}</p>
                    <p className="text-sm text-gray-400">{new Date(item.created_at).toLocaleString()}</p>
                  </div>
                  <span className={`rounded-full px-3 py-1 text-xs font-semibold ${item.severity === 'Critical' ? 'bg-red-500/20 text-red-200' : item.severity === 'High' ? 'bg-yellow-500/20 text-yellow-100' : 'bg-green-500/20 text-green-100'}`}>
                    {item.condition}
                  </span>
                </div>
                <button type="button" onClick={() => setReport(item)} className="mt-3 text-sm font-semibold text-aqua">View</button>
              </div>
            )) : <p className="rounded-2xl border border-white/10 bg-white/5 p-4 text-sm text-slate-400">No patient reports yet.</p>}
          </div>
        </div>
      </div>

      <div className="mt-6 card-surface rounded-[2rem] p-6 shadow-glow">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.35em] text-aqua">Patient Report</p>
            <h2 className="mt-2 font-display text-3xl font-bold text-white">Structured AI health report</h2>
            <p className="mt-2 max-w-2xl text-slate-300">Generate a validated report with patient info, vitals, diagnosis, alerts, insights, and a recommendation.</p>
          </div>
          <button onClick={handleGenerateReport} disabled={reportLoading} className="rounded-full bg-gradient-to-r from-aqua to-ocean px-5 py-3 text-sm font-semibold text-white shadow-glow transition hover:brightness-110 disabled:opacity-70">
            {reportLoading ? 'Generating report...' : 'Generate Report'}
          </button>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <label className="block">
            <span className="mb-2 block text-sm text-slate-400">Patient Name</span>
            <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={patientForm.name} onChange={(e) => setPatientForm({ ...patientForm, name: e.target.value })} />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm text-slate-400">Patient ID</span>
            <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={patientForm.id} onChange={(e) => setPatientForm({ ...patientForm, id: e.target.value })} />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm text-slate-400">Heart Rate</span>
            <input type="number" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={patientForm.heart_rate} onChange={(e) => setPatientForm({ ...patientForm, heart_rate: Number(e.target.value) })} />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm text-slate-400">BP (Systolic)</span>
            <input type="number" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={patientForm.bp_systolic} onChange={(e) => setPatientForm({ ...patientForm, bp_systolic: Number(e.target.value) })} />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm text-slate-400">BP (Diastolic)</span>
            <input type="number" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={patientForm.bp_diastolic} onChange={(e) => setPatientForm({ ...patientForm, bp_diastolic: Number(e.target.value) })} />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm text-slate-400">Temperature (°C)</span>
            <input type="number" step="0.1" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={patientForm.temperature} onChange={(e) => setPatientForm({ ...patientForm, temperature: Number(e.target.value) })} />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm text-slate-400">SpO2</span>
            <input type="number" step="0.1" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={patientForm.spo2} onChange={(e) => setPatientForm({ ...patientForm, spo2: Number(e.target.value) })} />
          </label>
          <label className="block">
            <span className="mb-2 block text-sm text-slate-400">ECG</span>
            <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={patientForm.ecg} onChange={(e) => setPatientForm({ ...patientForm, ecg: e.target.value })} />
          </label>
        </div>

        {reportError ? <p className="mt-5 rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{reportError}</p> : null}
        <div className="mt-6">
          <ReportGrid report={report} />
        </div>
      </div>

      {showHistory ? (
        <div className="mt-6 card-surface rounded-3xl p-5 shadow-glow">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <p className="text-sm uppercase tracking-[0.26em] text-slate-400">History</p>
              <h3 className="font-display text-xl text-white">Past predictions</h3>
            </div>
            <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-300">{history.length} records</span>
          </div>
          <div className="overflow-hidden rounded-2xl border border-white/10">
            <table className="w-full text-left text-sm">
              <thead className="bg-white/5 text-slate-300">
                <tr>
                  <th className="px-4 py-3 font-medium">Date</th>
                  <th className="px-4 py-3 font-medium">Location</th>
                  <th className="px-4 py-3 font-medium">Risk</th>
                  <th className="px-4 py-3 font-medium">Disease</th>
                  <th className="px-4 py-3 font-medium">AQI</th>
                </tr>
              </thead>
              <tbody>
                {history.length ? (
                  history.map((item) => (
                    <tr key={item.id} className="border-t border-white/10 text-slate-200">
                      <td className="px-4 py-3">{new Date(item.created_at).toLocaleString()}</td>
                      <td className="px-4 py-3">{item.location}</td>
                      <td className="px-4 py-3">{item.risk || item.risk_level}</td>
                      <td className="px-4 py-3">{item.disease}</td>
                      <td className="px-4 py-3">{item.aqi}</td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td className="px-4 py-5 text-slate-400" colSpan="5">
                      No prediction history yet. Run a prediction to save your first record.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      ) : null}
    </div>
  )
}
