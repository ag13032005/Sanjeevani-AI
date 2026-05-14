import { Link, NavLink } from 'react-router-dom'
import { useAuth } from '../context/useAuth'

const linkClass = ({ isActive }) =>
  `rounded-full px-4 py-2 text-sm font-medium transition ${isActive ? 'bg-white/12 text-white' : 'text-slate-300 hover:text-white'}`

export default function Navbar() {
  const { user, logout } = useAuth()

  return (
    <header className="sticky top-0 z-20 border-b border-white/10 bg-slate-950/60 backdrop-blur-xl">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link to="/dashboard" className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-aqua to-ocean text-lg font-black text-white shadow-glow">
            O
          </div>
          <div>
            <p className="font-display text-lg font-semibold text-white">Sanjeevani</p>
            <p className="text-xs uppercase tracking-[0.28em] text-slate-400">Early Warning System</p>
          </div>
        </Link>

        <nav className="hidden items-center gap-2 md:flex">
          <NavLink to="/dashboard" className={linkClass}>Dashboard</NavLink>
          <NavLink to="/map" className={linkClass}>Map</NavLink>
          <NavLink to="/submit-report" className={linkClass}>Submit Report</NavLink>
        </nav>

        <div className="flex items-center gap-3">
          {user ? <span className="hidden text-sm text-slate-300 sm:block">{user.name}</span> : null}
          <button
            type="button"
            onClick={logout}
            className="rounded-full border border-white/15 px-4 py-2 text-sm font-semibold text-white transition hover:border-white/30 hover:bg-white/10"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
