/// <reference types="google.maps" />

import { useEffect, useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { MapPin, AlertTriangle } from 'lucide-react'

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
  rose: { color: '#f43f5e' },
  amber: { color: '#fbbf24' },
  blue: { color: '#22d3ee' },
  violet: { color: '#a78bfa' },
}

export function GoogleMap({
  crises,
  onSelectCrisis,
  scanningCrisis,
}: GoogleMapProps) {

  const mapRef = useRef<HTMLDivElement>(null)

  const [map, setMap] = useState<google.maps.Map | null>(null)
  const [markers, setMarkers] = useState<google.maps.Marker[]>([])
  const [isLoaded, setIsLoaded] = useState(false)
  const [loadError, setLoadError] = useState<string | null>(null)

  const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY


  // LOAD GOOGLE MAPS
  useEffect(() => {
    if (!apiKey || !mapRef.current) return

    if (window.google?.maps) {
      initializeMap()
      return
    }

    const script = document.createElement('script')

    script.src =
      `https://maps.googleapis.com/maps/api/js?key=${apiKey}`

    script.async = true
    script.defer = true

    script.onload = () => {
      initializeMap()
    }

    script.onerror = () => {
      setLoadError('Failed to load Google Maps')
    }

    document.head.appendChild(script)


    function initializeMap() {
      if (!mapRef.current) return

      const mapInstance = new google.maps.Map(
        mapRef.current,
        {
          center: {
            lat: 20,
            lng: 0,
          },
          zoom: 2,

          styles: [
            {
              elementType: 'geometry',
              stylers: [{ color: '#0d141f' }],
            },
            {
              elementType: 'labels.text.fill',
              stylers: [{ color: '#5f93a5' }],
            },
            {
              featureType: 'water',
              elementType: 'geometry',
              stylers: [{ color: '#0d141f' }],
            },
          ],

          disableDefaultUI: true,
          zoomControl: true,
        }
      )

      setMap(mapInstance)
      setIsLoaded(true)
    }

  }, [apiKey])



  // MARKERS
  useEffect(() => {

    if (!map || !isLoaded) return


    markers.forEach(marker => {
      marker.setMap(null)
    })


    const newMarkers: google.maps.Marker[] = []


    crises.forEach((crisis,index)=>{

      const colors =
        colorMap[
          crisis.tone as keyof typeof colorMap
        ] || colorMap.blue


      const marker =
        new google.maps.Marker({

          position:{
            lat: crisis.lat,
            lng: crisis.lng
          },

          map,

          title: crisis.title,

          icon:{
            path:
              google.maps.SymbolPath.CIRCLE,

            scale:10,

            fillColor:colors.color,

            fillOpacity:0.9,

            strokeColor:colors.color,

            strokeWeight:2,
          }

        })


      marker.addListener(
        'click',
        ()=>{

          onSelectCrisis(index)

        }
      )


      newMarkers.push(marker)

    })


    setMarkers(newMarkers)


    return ()=>{
      newMarkers.forEach(marker=>{
        marker.setMap(null)
      })
    }


  },[
    map,
    crises,
    isLoaded,
    onSelectCrisis
  ])




  // SCAN ANIMATION
  useEffect(()=>{

    if(!map || !scanningCrisis)
      return


    const x =
      parseFloat(
        scanningCrisis.x.replace('%','')
      )

    const y =
      parseFloat(
        scanningCrisis.y.replace('%','')
      )


    if(!isNaN(x)&&!isNaN(y)){

      const lat =
        80 - (y/100)*140

      const lng =
        (x/100)*360 - 180


      map.panTo({
        lat,
        lng
      })

      map.setZoom(5)

    }

  },[
    scanningCrisis,
    map
  ])





  if(loadError){

    return (
      <div className="flex h-full items-center justify-center bg-[#0d141f]">

        <div className="text-center">

          <AlertTriangle className="mx-auto size-12 text-amber-400 mb-4"/>

          <p className="text-sm text-slate-400">
            {loadError}
          </p>

        </div>

      </div>
    )

  }



  if(!apiKey){

    return (
      <div className="flex h-full items-center justify-center bg-[#0d141f]">

        <div className="text-center">

          <MapPin className="mx-auto size-12 text-cyan-400 mb-4"/>

          <p className="text-sm text-slate-400">
            Google Maps API key not configured
          </p>

        </div>

      </div>
    )

  }



  return (

    <div className="relative h-full w-full">

      {!isLoaded && (

        <div className="absolute inset-0 flex items-center justify-center bg-[#0d141f]">

          <motion.div
            animate={{
              rotate:360
            }}
            transition={{
              duration:2,
              repeat:Infinity
            }}
            className="size-12 rounded-full border-4 border-cyan-400 border-t-transparent"
          />

        </div>

      )}

      <div
        ref={mapRef}
        className="h-full w-full"
      />

    </div>

  )
}