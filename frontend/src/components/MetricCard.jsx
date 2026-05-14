export default function MetricCard({ label, value, helper, accent = 'from-aqua to-ocean' }) {
  return (
    <div className="rounded-2xl bg-gradient-to-br from-slate-900 to-slate-800 p-5 shadow-lg">
      <div className={`mb-4 h-1.5 w-16 rounded-full bg-gradient-to-r ${accent}`} />
      <p className="text-sm uppercase tracking-[0.26em] text-gray-400">{label}</p>
      <p className="mt-3 font-display text-3xl font-bold text-white">{value}</p>
      <p className="mt-2 text-sm leading-6 text-gray-400">{helper}</p>
    </div>
  )
}
