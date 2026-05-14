import ReportCard from './ReportCard'

export default function ReportList({ reports = [], onView }) {
  if (!reports.length) {
    return <p className="rounded-2xl border border-white/10 bg-white/5 p-5 text-sm text-gray-400">No patient reports submitted yet.</p>
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {reports.map((report) => (
        <ReportCard key={report.id} report={report} onView={onView} />
      ))}
    </div>
  )
}