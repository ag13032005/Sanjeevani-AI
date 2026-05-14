import { useEffect, useState } from 'react'
import ReportForm from '../components/reports/ReportForm'
import ReportList from '../components/reports/ReportList'
import { getReports, submitReport, uploadReport } from '../services/api'

export default function MedicalReportPage() {
  const [reports, setReports] = useState([])
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  const loadReports = async () => {
    try {
      const data = await getReports()
      setReports(data)
    } catch {
      setReports([])
    }
  }

  useEffect(() => {
    loadReports()
  }, [])

  const handleSubmit = async (form) => {
    setBusy(true)
    setError('')
    setMessage('')
    try {
      await submitReport(form)
      setMessage('Report submitted successfully.')
      await loadReports()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to submit report')
    } finally {
      setBusy(false)
    }
  }

  const handleUpload = async (form, file) => {
    if (!file) {
      setError('Please choose a JPG, PNG, or PDF file first.')
      return
    }
    setBusy(true)
    setError('')
    setMessage('')
    try {
      const formData = new FormData()
      Object.entries(form).forEach(([key, value]) => formData.append(key, value))
      formData.append('file', file)
      await uploadReport(formData)
      setMessage('Report file uploaded successfully.')
      await loadReports()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to upload report file')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="card-surface rounded-[2rem] p-6 shadow-glow">
        <p className="text-sm uppercase tracking-[0.35em] text-aqua">Submit Medical Report</p>
        <h1 className="mt-3 font-display text-3xl font-bold text-white">Create and upload patient reports</h1>
        <p className="mt-2 text-slate-300">Enter patient vitals, generate a report, and optionally upload MRI, CT, or PDF evidence.</p>

        {message ? <p className="mt-5 rounded-2xl border border-emerald-400/30 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-100">{message}</p> : null}
        {error ? <p className="mt-5 rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">{error}</p> : null}

        <div className="mt-6">
          <ReportForm onSubmit={handleSubmit} onUpload={handleUpload} busy={busy} />
        </div>
      </div>

      <div className="mt-6 card-surface rounded-[2rem] p-6 shadow-glow">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.35em] text-aqua">Patient Reports</p>
            <h2 className="mt-2 font-display text-2xl font-bold text-white">Submitted reports</h2>
          </div>
          <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-300">{reports.length} total</span>
        </div>
        <ReportList reports={reports} />
      </div>
    </div>
  )
}