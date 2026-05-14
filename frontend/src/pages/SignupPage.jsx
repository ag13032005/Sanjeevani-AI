import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

export default function SignupPage() {
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const { signup } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (event) => {
    event.preventDefault()
    setLoading(true)
    setError('')
    try {
      await signup(form)
      navigate('/dashboard')
    } catch (err) {
      setError(err?.response?.data?.detail || 'Unable to create account')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4 py-10">
      <form onSubmit={handleSubmit} className="card-surface w-full max-w-lg rounded-[2rem] p-8 shadow-glow">
        <p className="text-sm uppercase tracking-[0.35em] text-aqua">Get started</p>
        <h1 className="mt-4 font-display text-4xl font-bold text-white">Create your Sanjeevani account</h1>
        <p className="mt-2 text-slate-300">Use one workspace to keep predictions, alerts, and location history together.</p>
        <div className="mt-8 space-y-5">
          <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none placeholder:text-slate-500" placeholder="Full name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none placeholder:text-slate-500" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none placeholder:text-slate-500" placeholder="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
          {error ? <p className="rounded-2xl border border-rose-400/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">{error}</p> : null}
          <button disabled={loading} className="w-full rounded-2xl bg-gradient-to-r from-ember to-ocean px-4 py-3 font-semibold text-white shadow-glow transition hover:brightness-110 disabled:opacity-70" type="submit">
            {loading ? 'Creating account...' : 'Signup'}
          </button>
        </div>
        <p className="mt-6 text-sm text-slate-300">
          Already registered? <Link className="font-semibold text-aqua" to="/login">Login here</Link>.
        </p>
      </form>
    </div>
  )
}
