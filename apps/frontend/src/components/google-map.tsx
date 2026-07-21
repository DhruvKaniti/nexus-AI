/// <reference types="google.maps" />
import { useEffect, useRef, useState } from 'react'
import { Loader } from '@googlemaps/js-api-loader'
import { motion } from 'framer-motion'
import { MapPin, AlertTriangle} from 'lucide-react'

interface Crisis {
  title: string
  place: string
  severity: string
  tone: string
  time: string
  lat: number
  lng: number
}

interface GoogleMapProps {
  crises: Crisis[]
  onSelectCrisis: (index: number) => void
  selectedCrisis: number | null
  scanningCrisis?: { x: string; y: string } | null
}

const colorMap = {
  rose: { color: '#f43f5e', bgColor: 'rgba(244, 63, 94, 0.2)' },
  amber: { color: '#fbbf24', bgColor: 'rgba(251, 191, 36, 0.2)' },
  blue: { color: '#22d3ee', bgColor: 'rgba(34, 211, 238, 0.2)' },
  violet: { color: '#a78bfa', bgColor: 'rgba(167, 139, 250, 0.2)' },
}

export function GoogleMap({ crises, onSelectCrisis, scanningCrisis }: GoogleMapProps){
  const mapRef = useRef<HTMLDivElement>(null)
  const [map, setMap] = useState<google.maps.Map | null>(null)
  const [markers, setMarkers] = useState<google.maps.Marker[]>([])
  const [isLoaded, setIsLoaded] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)

  // Get API key from environment
  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY

  // Initialize map
  useEffect(() => {
    if (!apiKey || !mapRef.current) return

    const loader = new Loader({
      apiKey: apiKey,
      version: 'weekly',
      libraries: ['places'],
    })

    loader
      .load()
      .then(() => {
        if (!mapRef.current) return

        const mapInstance = new google.maps.Map(mapRef.current, {
          center: { lat: 20, lng: 0 },
          zoom: 2,
          styles: [
            { elementType: 'geometry', stylers: [{ color: '#0d141f' }] },
            { elementType: 'labels.text.stroke', stylers: [{ color: '#0d141f' }] },
            { elementType: 'labels.text.fill', stylers: [{ color: '#5f93a5' }] },
            { featureType: 'administrative', elementType: 'geometry.stroke', stylers: [{ color: '#1a3342' }] },
            { featureType: 'administrative.land_parcel', elementType: 'labels.text.fill', stylers: [{ color: '#5f93a5' }] },
            { featureType: 'poi', elementType: 'geometry', stylers: [{ color: '#1a3342' }] },
            { featureType: 'poi', elementType: 'labels.text.fill', stylers: [{ color: '#5f93a5' }] },
            { featureType: 'poi.park', elementType: 'geometry', stylers: [{ color: '#1a3342' }] },
            { featureType: 'road', elementType: 'geometry', stylers: [{ color: '#1a3342' }] },
            { featureType: 'road', elementType: 'geometry.stroke', stylers: [{ color: '#0d141f' }] },
            { featureType: 'road.highway', elementType: 'geometry', stylers: [{ color: '#1a3342' }] },
            { featureType: 'road.highway', elementType: 'geometry.stroke', stylers: [{ color: '#0d141f' }] },
            { featureType: 'transit', elementType: 'geometry', stylers: [{ color: '#1a3342' }] },
            { featureType: 'transit.station', elementType: 'labels.text.fill', stylers: [{ color: '#5f93a5' }] },
            { featureType: 'water', elementType: 'geometry', stylers: [{ color: '#0d141f' }] },
            { featureType: 'water', elementType: 'labels.text.fill', stylers: [{ color: '#5f93a5' }] },
          ],
          disableDefaultUI: true,
          zoomControl: true,
          mapTypeControl: false,
          streetViewControl: false,
          fullscreenControl: false,
        })

        setMap(mapInstance)
        setIsLoaded(true)
      })
      .catch((error) => {
        console.error('Error loading Google Maps:', error)
        setLoadError('Failed to load Google Maps. Please check your API key.')
      })

    return () => {
      // Cleanup markers
      markers.forEach((marker) => marker.setMap(null))
    }
  }, [apiKey])

  // Update markers when crises change
  useEffect(() => {
    if (!map || !isLoaded) return

    // Clear existing markers
    markers.forEach((marker) => marker.setMap(null))

    // Create new markers
    const newMarkers: google.maps.Marker[] = []

    crises.forEach((crisis, index) => {
      const colors = colorMap[crisis.tone as keyof typeof colorMap] || colorMap.blue

      const marker = new google.maps.Marker({
        position: { lat: crisis.lat, lng: crisis.lng },
        map: map,
        title: crisis.title,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: 10,
          fillColor: colors.color,
          fillOpacity: 0.9,
          strokeColor: colors.color,
          strokeWeight: 2,
        },
        animation: google.maps.Animation.DROP,
      })

      // Create info window content
      const infoContent = `
        <div style="
          background: #101925;
          border: 1px solid ${colors.color}40;
          border-radius: 12px;
          padding: 12px;
          min-width: 200px;
          box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        ">
          <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <div style="
              width: 8px;
              height: 8px;
              border-radius: 50%;
              background: ${colors.color};
              box-shadow: 0 0 10px ${colors.color};
            "></div>
            <h3 style="
              margin: 0;
              font-size: 14px;
              font-weight: 600;
              color: #f1f5f9;
              font-family: system-ui, -apple-system, sans-serif;
            ">${crisis.title}</h3>
          </div>
          <div style="
            font-size: 12px;
            color: #94a3b8;
            margin-bottom: 8px;
            font-family: system-ui, -apple-system, sans-serif;
          ">${crisis.place}</div>
          <div style="
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding-top: 8px;
            border-top: 1px solid rgba(255,255,255,0.1);
          ">
            <span style="
              font-size: 10px;
              color: #64748b;
              font-family: system-ui, -apple-system, sans-serif;
            ">${crisis.time}</span>
            <span style="
              font-size: 10px;
              font-weight: 600;
              color: ${colors.color};
              text-transform: uppercase;
              letter-spacing: 0.05em;
              font-family: system-ui, -apple-system, sans-serif;
            ">${crisis.severity}</span>
          </div>
        </div>
      `

      const infoWindowInstance = new google.maps.InfoWindow({
        content: infoContent,
        maxWidth: 300,
      })

      marker.addListener('click', () => {
        infoWindowInstance.open(map, marker)
        onSelectCrisis(index)
      })

      newMarkers.push(marker)
    })

    setMarkers(newMarkers)

    return () => {
      newMarkers.forEach((marker) => marker.setMap(null))
    }
  }, [map, crises, isLoaded, onSelectCrisis])

  // Handle scanning animation
  useEffect(() => {
    if (!map || !scanningCrisis) return

    // You can add a pulsing marker or circle here for scanning effect
    // For now, we'll just center the map on the scanning location
    const lng = parseFloat(scanningCrisis.x.replace('%', ''))
    const lat = parseFloat(scanningCrisis.y.replace('%', ''))

    if (!isNaN(lng) && !isNaN(lat)) {
      // Convert percentage back to lat/lng (approximate)
      const latVal = 80 - (lat / 100) * 140
      const lngVal = (lng / 100) * 360 - 180

      map.panTo({ lat: latVal, lng: lngVal })
      map.setZoom(5)
    }
  }, [scanningCrisis, map])

  if (loadError) {
    return (
      <div className="flex h-full items-center justify-center bg-[#0d141f]">
        <div className="text-center">
          <AlertTriangle className="mx-auto size-12 text-amber-400 mb-4" />
          <p className="text-sm text-slate-400">{loadError}</p>
          <p className="text-xs text-slate-500 mt-2">Please add VITE_GOOGLE_MAPS_API_KEY to your .env file</p>
        </div>
      </div>
    )
  }

  if (!apiKey) {
    return (
      <div className="flex h-full items-center justify-center bg-[#0d141f]">
        <div className="text-center">
          <MapPin className="mx-auto size-12 text-cyan-400 mb-4" />
          <p className="text-sm text-slate-400">Google Maps API key not configured</p>
          <p className="text-xs text-slate-500 mt-2">Add VITE_GOOGLE_MAPS_API_KEY to your .env file</p>
        </div>
      </div>
    )
  }

  return (
    <div className="relative h-full w-full">
      {!isLoaded && (
        <div className="absolute inset-0 flex items-center justify-center bg-[#0d141f]">
          <div className="text-center">
            <div className="relative size-16 mx-auto mb-4">
              <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                className="absolute inset-0 rounded-full border-4 border-cyan-400 border-t-transparent"
              />
            </div>
            <p className="text-sm text-slate-400">Loading map...</p>
          </div>
        </div>
      )}
      <div ref={mapRef} className="h-full w-full" />
    </div>
  )
}