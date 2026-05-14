export default function ReportCard({ report, onView }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-gradient-to-br from-slate-900 to-slate-800 p-5 shadow-lg">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm text-gray-400">{new Date(report.created_at).toLocaleString()}</p>
          <h4 className="mt-1 font-display text-lg font-semibold text-white">{report.patient_name}</h4>
          <p className="mt-1 text-sm text-gray-400">Condition: {report.condition}</p>
        </div>
        <span className={`rounded-full px-3 py-1 text-xs font-semibold ${report.severity === 'Critical' ? 'bg-red-500/20 text-red-200' : report.severity === 'High' ? 'bg-yellow-500/20 text-yellow-100' : 'bg-green-500/20 text-green-100'}`}>
          {report.severity}
        </span>
      </div>

      <div className="mt-4 grid gap-2 text-sm text-gray-300">
        <p>Age: {report.age}</p>
        <p>Vitals: {report.vitals?.heart_rate} bpm, BP {report.vitals?.bp}, SpO2 {report.vitals?.spo2}%</p>
        <p>ECG: {report.vitals?.ecg}</p>
      </div>

      <button
        onClick={() => onView?.(report)}
        className="mt-4 rounded-xl border border-white/10 bg-white/5 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/10"
      >
        View
      </button>
    </div>
  )
}