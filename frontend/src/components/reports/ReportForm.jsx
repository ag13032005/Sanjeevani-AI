import { useState } from 'react'
import FileUpload from './FileUpload'

const initialForm = {
  patient_name: '',
  age: 45,
  heart_rate: 82,
  bp_systolic: 128,
  bp_diastolic: 82,
  temperature: 36.8,
  spo2: 98,
  ecg: 'Normal Sinus Rhythm',
  notes: '',
}

export default function ReportForm({ onSubmit, onUpload, busy = false }) {
  const [form, setForm] = useState(initialForm)
  const [file, setFile] = useState(null)

  const updateField = (field, value) => setForm((current) => ({ ...current, [field]: value }))

  const handleSubmit = async (event) => {
    event.preventDefault()
    await onSubmit(form)
  }

  const handleUpload = async (event) => {
    event.preventDefault()
    await onUpload(form, file)
  }

  return (
    <form className="space-y-5" onSubmit={handleSubmit}>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <label className="block"><span className="mb-2 block text-sm text-gray-400">Patient Name</span><input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={form.patient_name} onChange={(e) => updateField('patient_name', e.target.value)} /></label>
        <label className="block"><span className="mb-2 block text-sm text-gray-400">Age</span><input type="number" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={form.age} onChange={(e) => updateField('age', Number(e.target.value))} /></label>
        <label className="block"><span className="mb-2 block text-sm text-gray-400">Heart Rate</span><input type="number" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={form.heart_rate} onChange={(e) => updateField('heart_rate', Number(e.target.value))} /></label>
        <label className="block"><span className="mb-2 block text-sm text-gray-400">BP (Systolic)</span><input type="number" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={form.bp_systolic} onChange={(e) => updateField('bp_systolic', Number(e.target.value))} /></label>
        <label className="block"><span className="mb-2 block text-sm text-gray-400">BP (Diastolic)</span><input type="number" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={form.bp_diastolic} onChange={(e) => updateField('bp_diastolic', Number(e.target.value))} /></label>
        <label className="block"><span className="mb-2 block text-sm text-gray-400">Temperature (°C)</span><input type="number" step="0.1" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={form.temperature} onChange={(e) => updateField('temperature', Number(e.target.value))} /></label>
        <label className="block"><span className="mb-2 block text-sm text-gray-400">SpO2</span><input type="number" step="0.1" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={form.spo2} onChange={(e) => updateField('spo2', Number(e.target.value))} /></label>
        <label className="block"><span className="mb-2 block text-sm text-gray-400">ECG</span><input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={form.ecg} onChange={(e) => updateField('ecg', e.target.value)} /></label>
      </div>

      <label className="block">
        <span className="mb-2 block text-sm text-gray-400">Notes</span>
        <textarea rows="4" className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={form.notes} onChange={(e) => updateField('notes', e.target.value)} />
      </label>

      <FileUpload file={file} setFile={setFile} />

      <div className="flex flex-wrap gap-3">
        <button disabled={busy} type="submit" className="rounded-xl bg-aqua px-5 py-3 font-semibold text-slate-950 transition hover:brightness-110 disabled:opacity-70">Submit Report</button>
        <button disabled={busy || !file} type="button" onClick={handleUpload} className="rounded-xl border border-white/15 bg-white/5 px-5 py-3 font-semibold text-white transition hover:bg-white/10 disabled:opacity-60">Upload Report File</button>
      </div>
    </form>
  )
}