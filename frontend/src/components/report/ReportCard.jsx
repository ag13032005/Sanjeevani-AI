export default function ReportCard({ title, icon, value, detail, tone = 'normal' }) {
  const toneClasses = {
    normal: 'border-white/10 bg-white/5 text-white',
    warning: 'border-amber-400/25 bg-amber-500/10 text-amber-100',
    critical: 'border-rose-400/30 bg-rose-500/10 text-rose-100',
    success: 'border-emerald-400/25 bg-emerald-500/10 text-emerald-100',
  }

  return (
    <div className={`card-surface rounded-3xl border p-5 shadow-glow ${toneClasses[tone] || toneClasses.normal}`}>
      <div className="mb-3 flex items-center gap-2 text-sm uppercase tracking-[0.25em] text-slate-400">
        <span>{icon}</span>
        <span>{title}</span>
      </div>
      <p className="font-display text-2xl font-bold">{value}</p>
      <p className="mt-2 text-sm leading-6 text-slate-300">{detail}</p>
    </div>
  )
}
