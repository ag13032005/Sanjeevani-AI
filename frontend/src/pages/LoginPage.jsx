import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

export default function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      await login({ email, password })
      navigate('/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to login')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <div className="grid w-full max-w-5xl gap-8 lg:grid-cols-[1.15fr_0.85fr]">
        <div className="rounded-[2rem] border border-white/10 bg-white/5 p-8 shadow-glow backdrop-blur-xl">
          <p className="text-sm uppercase tracking-[0.35em] text-aqua">Sanjeevani</p>
          <h1 className="mt-4 font-display text-4xl font-bold text-white sm:text-5xl">Track outbreak risk before it spikes.</h1>
          <p className="mt-5 max-w-xl text-lg leading-8 text-slate-300">
            Log in to inspect weather-driven disease risk, see live AQI and humidity signals, and store your prediction history.
          </p>
          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            {[
              ['AI', 'Random Forest risk engine'],
              ['Maps', 'Leaflet risk zones'],
              ['History', 'Saved per user in MongoDB'],
            ].map(([title, text]) => (
              <div key={title} className="rounded-3xl border border-white/10 bg-slate-950/60 p-4">
                <p className="font-display text-xl text-white">{title}</p>
                <p className="mt-2 text-sm text-slate-300">{text}</p>
              </div>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit} className="card-surface rounded-[2rem] p-8 shadow-glow">
          <h2 className="font-display text-3xl text-white">Welcome back</h2>
          <p className="mt-2 text-slate-300">Sign in to continue to the dashboard.</p>
          <div className="mt-8 space-y-5">
            <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none placeholder:text-slate-500" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} />
            <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none placeholder:text-slate-500" placeholder="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            {error ? <p className="rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</p> : null}
            <button disabled={loading} className="w-full rounded-2xl bg-gradient-to-r from-aqua to-ocean px-4 py-3 font-semibold text-white shadow-glow transition hover:brightness-110 disabled:opacity-70" type="submit">
              {loading ? 'Signing in...' : 'Login'}
            </button>
          </div>
          <p className="mt-6 text-sm text-slate-300">
            Need an account? <Link className="font-semibold text-aqua" to="/signup">Create one here</Link>.
          </p>
        </form>
      </div>
    </div>
  )
}
