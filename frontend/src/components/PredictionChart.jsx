import {
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

function getRiskScore(riskLevel, confidence) {
  if (typeof confidence === 'number') {
    return Math.max(0, Math.min(100, Math.round(confidence * 100)))
  }

  const scoreMap = { Low: 25, Medium: 60, High: 90 }
  return scoreMap[riskLevel] || 0
}

export default function PredictionChart({ history }) {
  const sortedHistory = [...history].sort((left, right) => new Date(left.created_at) - new Date(right.created_at)).slice(-50)
  const labels = sortedHistory.map((item) => new Date(item.created_at).toLocaleString())
  const values = sortedHistory.map((item) => getRiskScore(item.risk || item.risk_level, item.confidence))

  const data = {
    labels,
    datasets: [
      {
        label: 'Risk score / confidence',
        data: values,
        borderColor: '#1bb3a7',
        backgroundColor: 'rgba(27, 179, 167, 0.25)',
        tension: 0.35,
        fill: true,
        pointRadius: 4,
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { labels: { color: '#dbeafe' } },
    },
    scales: {
      x: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.12)' } },
      y: { ticks: { color: '#94a3b8' }, grid: { color: 'rgba(148,163,184,0.12)' } },
    },
  }

  return (
    <div className="card-surface h-[320px] rounded-3xl p-5 shadow-glow">
      <div className="mb-4 flex items-end justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.26em] text-slate-400">Trend</p>
          <h3 className="font-display text-xl text-white">Prediction history</h3>
        </div>
        <span className="rounded-full bg-white/10 px-3 py-1 text-xs text-slate-300">Last {sortedHistory.length} checks</span>
      </div>
      <div className="h-[240px]">
        <Line data={data} options={options} />
      </div>
    </div>
  )
}
