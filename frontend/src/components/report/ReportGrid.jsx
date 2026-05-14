import ReportCard from './ReportCard'

export default function ReportGrid({ report }) {
  if (!report) {
    return null
  }

  const { patient, vitals, diagnosis, insights, alerts, recommendation } = report

  return (
    <div className="space-y-6">
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        <ReportCard
          title="Patient Info"
          icon="🧾"
          value={patient.name}
          detail={`ID: ${patient.id} · Date: ${patient.date}`}
        />
        <ReportCard
          title="Vital Signs"
          icon="❤️"
          value={`${vitals.heart_rate} bpm · ${vitals.bp}`}
          detail={`Temp: ${vitals.temperature}°C · SpO2: ${vitals.spo2}% · ECG: ${vitals.ecg}`}
        />
        <ReportCard
          title="AI Diagnosis"
          icon="🧠"
          value={`${diagnosis.condition} (${diagnosis.severity})`}
          detail={`Confidence: ${diagnosis.confidence}%`}
          tone={diagnosis.severity === 'Critical' ? 'critical' : diagnosis.severity === 'High' ? 'warning' : 'success'}
        />
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <div className="card-surface rounded-3xl border border-rose-400/25 bg-rose-500/10 p-5 shadow-glow">
          <div className="mb-3 flex items-center gap-2 text-sm uppercase tracking-[0.25em] text-rose-200">
            <span>⚠️</span>
            <span>Alerts</span>
          </div>
          <ul className="space-y-2 text-sm text-rose-50">
            {alerts.length ? alerts.map((item) => <li key={item}>• {item}</li>) : <li>• No critical alerts detected.</li>}
          </ul>
        </div>

        <div className="card-surface rounded-3xl border border-white/10 bg-white/5 p-5 shadow-glow">
          <div className="mb-3 flex items-center gap-2 text-sm uppercase tracking-[0.25em] text-slate-400">
            <span>📊</span>
            <span>Insights</span>
          </div>
          <ul className="space-y-2 text-sm text-slate-200">
            {insights.length ? insights.map((item) => <li key={item}>• {item}</li>) : <li>• No insights available.</li>}
          </ul>
        </div>
      </div>

      <div className="card-surface rounded-3xl border border-emerald-400/25 bg-emerald-500/10 p-5 shadow-glow">
        <div className="mb-3 flex items-center gap-2 text-sm uppercase tracking-[0.25em] text-emerald-100">
          <span>💡</span>
          <span>Recommendation</span>
        </div>
        <p className="text-sm leading-7 text-emerald-50">{recommendation}</p>
      </div>
    </div>
  )
}
