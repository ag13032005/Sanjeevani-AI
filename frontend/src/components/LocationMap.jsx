import { MapContainer, Marker, Popup, Circle, TileLayer, useMap } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import { useEffect } from 'react'

const defaultIcon = new L.Icon({
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
})

function Recenter({ center }) {
  const map = useMap()
  useEffect(() => {
    map.setView(center, map.getZoom())
  }, [center, map])
  return null
}

export default function LocationMap({ lat, lon, riskLevel }) {
  const center = [lat || 20.5937, lon || 78.9629]
  const color = riskLevel === 'High' ? '#ff8a5b' : riskLevel === 'Medium' ? '#f4c430' : '#8ed081'

  return (
    <div className="card-surface overflow-hidden rounded-3xl shadow-glow">
      <div className="border-b border-white/10 px-5 py-4">
        <p className="text-sm uppercase tracking-[0.26em] text-slate-400">Map</p>
        <h3 className="font-display text-xl text-white">Location and risk zone</h3>
      </div>
      <div className="h-[420px]">
        <MapContainer center={center} zoom={7} className="h-full w-full">
          <Recenter center={center} />
          <TileLayer
            attribution='&copy; OpenStreetMap contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker position={center} icon={defaultIcon}>
            <Popup>
              User location
              <br />
              Risk level: {riskLevel || 'Unknown'}
            </Popup>
          </Marker>
          <Circle center={center} radius={riskLevel === 'High' ? 35000 : riskLevel === 'Medium' ? 22000 : 12000} pathOptions={{ color, fillColor: color, fillOpacity: 0.18 }} />
        </MapContainer>
      </div>
    </div>
  )
}
