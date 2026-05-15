import { useEffect, useState } from 'react'
import LocationMap from '../components/LocationMap'
import { getHistory, getWeather, getAqi } from '../services/api'

const defaultLatitude = 19.076
const defaultLongitude = 72.8777

export default function MapPage() {
  const [lat, setLat] = useState(defaultLatitude)
  const [lon, setLon] = useState(defaultLongitude)
  const [riskLevel, setRiskLevel] = useState('Low')
  const [info, setInfo] = useState(null)

  useEffect(() => {
    if (!navigator.geolocation) {
      return
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLat(position.coords.latitude)
        setLon(position.coords.longitude)
      },
      () => {
        setLat(defaultLatitude)
        setLon(defaultLongitude)
      },
      { enableHighAccuracy: false, timeout: 10000, maximumAge: 600000 },
    )
  }, [])

  useEffect(() => {
    const refresh = async () => {
      try {
        const [weather, aqi, history] = await Promise.all([getWeather(lat, lon), getAqi(lat, lon), getHistory()])
        setInfo({ weather, aqi, historyCount: history.length })
        setRiskLevel(history[0]?.risk_level || 'Low')
      } catch {
        setInfo(null)
      }
    }
    refresh()
  }, [lat, lon])

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <div className="mb-6 grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
        <div className="card-surface rounded-[2rem] p-6 shadow-glow">
          <p className="text-sm uppercase tracking-[0.35em] text-aqua">Map view</p>
          <h1 className="mt-3 font-display text-3xl text-white">Risk zones by location</h1>
          <p className="mt-3 text-slate-300">
            The map centers on the selected coordinates and expands the risk zone based on the latest model result.
          </p>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <label>
              <span className="mb-2 block text-sm text-slate-400">Latitude</span>
              <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={lat} onChange={(e) => setLat(Number(e.target.value))} />
            </label>
            <label>
              <span className="mb-2 block text-sm text-slate-400">Longitude</span>
              <input className="w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none" value={lon} onChange={(e) => setLon(Number(e.target.value))} />
            </label>
          </div>
          <div className="mt-6 rounded-3xl border border-white/10 bg-white/5 p-5 text-sm text-slate-300">
            <p className="text-slate-400">Current risk</p>
            <p className="mt-2 text-xl font-semibold text-white">{riskLevel}</p>
            <p className="mt-2">{info ? `${info.weather.temperature.toFixed(1)}°C, AQI ${info.aqi.aqi}, ${info.historyCount} history records` : 'Loading live context...'}</p>
          </div>
        </div>
        <LocationMap lat={lat} lon={lon} riskLevel={riskLevel} onSelectLocation={(nextLat, nextLon) => {
          setLat(nextLat)
          setLon(nextLon)
        }} />
      </div>
    </div>
  )
}
