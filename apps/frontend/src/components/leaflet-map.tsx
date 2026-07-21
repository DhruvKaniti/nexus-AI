  import { useEffect, useMemo, useRef, useState } from 'react'
  import { motion } from 'framer-motion'
  import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
  import L from 'leaflet'
  import { MapPin, AlertTriangle } from 'lucide-react'

  // Haversine distance calculation for clustering
  function haversineDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
    const R = 6371 // Earth's radius in km
    const dLat = ((lat2 - lat1) * Math.PI) / 180
    const dLon = ((lon2 - lon1) * Math.PI) / 180
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) * Math.sin(dLon / 2)
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
    return R * c
  }

  // Fix for default marker icons in Leaflet with webpack/vite
  delete (L.Icon.Default.prototype as any)._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  })

  interface Crisis {
    title: string
    place: string
    severity: string
    tone: string
    time: string
    lat: number
    lng: number
  }

  interface LeafletMapProps {
    crises: Crisis[]
    onSelectCrisis: (index: number) => void
    selectedCrisis: number | null
    scanningCrisis?: { x: string; y: string } | null
  }

  const colorMap = {
    rose: { color: '#f43f5e', glowColor: 'rgba(244, 63, 94, 0.6)' },
    amber: { color: '#fbbf24', glowColor: 'rgba(251, 191, 36, 0.6)' },
    blue: { color: '#22d3ee', glowColor: 'rgba(34, 211, 238, 0.6)' },
    violet: { color: '#a78bfa', glowColor: 'rgba(167, 139, 250, 0.6)' },
  }

  // Custom marker icon
  function createCustomIcon(color: string, glowColor: string) {
    return L.divIcon({
      className: 'custom-marker',
      html: `
        <div style="
          position: relative;
          width: 24px;
          height: 24px;
        ">
          <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 16px;
            height: 16px;
            background: ${color};
            border-radius: 50%;
            box-shadow: 0 0 20px ${glowColor}, 0 0 40px ${glowColor};
            border: 2px solid ${color};
          "></div>
          <div style="
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: ${glowColor};
            opacity: 0.3;
            animation: pulse 2s ease-out infinite;
          "></div>
        </div>
      `,
      iconSize: [24, 24],
      iconAnchor: [12, 12],
    })
  }

  // Radar overlay component for military/intelligence style scanning effect
  function RadarOverlay({ isActive }: { isActive: boolean }) {
    if (!isActive) return null
    
    return (
      <div className="absolute inset-0 pointer-events-none overflow-hidden" style={{ zIndex: 9999 }}>
        {/* Concentric radar circles */}
        <div className="absolute left-1/2 top-1/2 h-64 w-64 -translate-x-1/2 -translate-y-1/2">
          {[1, 2, 3, 4].map((ring) => (
            <div
              key={ring}
              className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-400/50"
              style={{
                width: `${ring * 64}px`,
                height: `${ring * 64}px`,
                opacity: 0.5 - (ring * 0.1)
              }}
            />
          ))}
        </div>

        {/* Expanding radar pulses */}
        {[0, 1.5, 3].map((delay) => (
          <motion.div
            key={delay}
            className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full border border-cyan-400/70"
            initial={{ width: 0, height: 0, opacity: 0.6 }}
            animate={{
              width: 512,
              height: 512,
              opacity: 0,
            }}
            transition={{
              duration: 4,
              delay: delay,
              repeat: Infinity,
              ease: 'easeOut',
            }}
          />
        ))}

        {/* Center radar dot */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
          <div className="relative size-5">
            <div className="absolute inset-0 rounded-full bg-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.9)]" />
            <div className="absolute inset-0 animate-ping rounded-full bg-cyan-400/60" />
          </div>
        </div>

        {/* Grid overlay */}
        <div 
          className="absolute inset-0"
          style={{
            opacity: 0.08,
            backgroundImage: `
              linear-gradient(rgba(34, 211, 238, 0.8) 1px, transparent 1px),
              linear-gradient(90deg, rgba(34, 211, 238, 0.8) 1px, transparent 1px)
            `,
            backgroundSize: '50px 50px',
          }}
        />
      </div>
    )
  }


  // Demo crisis locations for initial scan animation
  const demoCrises = [
    { lat: 40.7128, lng: -74.0060 },  // New York
    { lat: 51.5074, lng: -0.1278 },   // London
    { lat: 35.6762, lng: 139.6503 },  // Tokyo
    { lat: -33.8688, lng: 151.2093 }, // Sydney
    { lat: 55.7558, lng: 37.6173 },   // Moscow
  ]

  // Component to handle map view changes and scanning animation
  function MapViewController({ center, zoom, crises, scanningCrisis }: { 
    center: [number, number]; 
    zoom: number; 
    crises: any[];
    scanningCrisis?: {x:string, y:string} | null;
  }) { 
    const map = useMap()

    useEffect(() => {
      // Get valid crises with coordinates
      const validCrises = crises.filter(c => 
        c && 
        typeof c.lat === "number" && 
        typeof c.lng === "number" && 
        !Number.isNaN(c.lat) && 
        !Number.isNaN(c.lng) &&
        (c.lat !== 0 || c.lng !== 0)
      )

      // Use demo crises if no real crises available yet
      const crisesToScan = validCrises.length > 0 ? validCrises : demoCrises

      let cancelled = false
      let animationInterval: ReturnType<typeof setInterval>

      // Helper function to get random crisis location
      const getRandomCrisis = () => {
        const randomIndex = Math.floor(Math.random() * crisesToScan.length)
        return crisesToScan[randomIndex]
      }

      async function runScanningAnimation() {
        // Initial zoom out to show overview
        if (cancelled) return
        map.flyTo([20, 0], 2, {
          duration: 2
        })

        await new Promise(r => setTimeout(r, 2000))
        if (cancelled) return

        // Periodic scanning animation - randomly select crisis locations
        animationInterval = setInterval(async () => {
          if (cancelled || crisesToScan.length === 0) {
            clearInterval(animationInterval)
            return
          }

          // Get random crisis to scan
          const crisis = getRandomCrisis()

          // Zoom in to crisis location
          map.flyTo([crisis.lat, crisis.lng], 8, {
            duration: 3
          })

          await new Promise(r => setTimeout(r, 4000))
          if (cancelled) return

          // Return to overview to show all markers
          map.flyTo([20, 0], 2, {
            duration: 3
          })

          await new Promise(r => setTimeout(r, 3000))
        }, 7000) // Repeat every 7 seconds
      }

      runScanningAnimation()

      return () => {
        cancelled = true
        if (animationInterval) {
          clearInterval(animationInterval)
        }
      }
    }, [map, crises])

    useEffect(() => {
      // Auto-fit bounds to show all markers
      const validCrises = crises.filter(c => c.lat !== 0 && c.lng !== 0)
      
      if (validCrises.length > 0) {
        const bounds = L.latLngBounds(validCrises.map(c => [c.lat, c.lng]))
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 })
      } else {
        map.setView(center, zoom)
      }
      
      map.invalidateSize()
    }, [map])
    
    return null
  }

  export function LeafletMap({ crises, onSelectCrisis, selectedCrisis, scanningCrisis }: LeafletMapProps) {
    const defaultCenter: [number, number] = [20, 0]
    const defaultZoom = 2
    const [isMapReady, setIsMapReady] = useState(false)
    const [isRadarActive, setIsRadarActive] = useState(true)
    
    // Stop radar after markers are loaded
    useEffect(() => {
      if (crises.length > 0 && isMapReady) {
        const timer = setTimeout(() => {
          setIsRadarActive(false)
        }, 5000) // Stop radar after 5 seconds once map is ready with data
        return () => clearTimeout(timer)
      }
    }, [crises.length, isMapReady])
    
    // Cluster crises that are within 100km of each other
    const clusteredCrises = useMemo(() => {
    const validCrises = crises.filter(
      (c) =>
        c &&
        typeof c.lat === "number" &&
        typeof c.lng === "number" &&
        !Number.isNaN(c.lat) &&
        !Number.isNaN(c.lng)
    )

    const clusters: Array<{ lat: number; lng: number; crises: any[] }> = []
    const assigned = new Set<number>()

    validCrises.forEach((crisis, i) => {
      if (assigned.has(i)) return

      const cluster = {
        lat: crisis.lat,
        lng: crisis.lng,
        crises: [crisis],
      }

      assigned.add(i)

      validCrises.forEach((other, j) => {
        if (i === j || assigned.has(j)) return

        const distance = haversineDistance(
          crisis.lat,
          crisis.lng,
          other.lat,
          other.lng
        )

        if (distance < 100) {
          cluster.crises.push(other)
          assigned.add(j)
        }
      })

      if (cluster.crises.length > 1) {
        cluster.lat =
          cluster.crises.reduce((s, c) => s + c.lat, 0) /
          cluster.crises.length

        cluster.lng =
          cluster.crises.reduce((s, c) => s + c.lng, 0) /
          cluster.crises.length
      }

      clusters.push(cluster)
    })

    return clusters
  }, [crises])
    
    // DEBUG: Log every time LeafletMap receives new crises
    console.log('🗺️ LeafletMap render - crises prop:', JSON.stringify(crises, null, 2))
    console.log(`   Total crises: ${crises.length}`)
    console.log(`   Clustered markers: ${clusteredCrises.length}`)
    console.log(`   Crisis titles: ${crises.map(c => c.title).join(', ')}`)
    
    // Calculate center based on crises
      const getMapCenter = (): [number, number] => {
        if (crises.length === 0) return defaultCenter
        
    const validCrises = crises.filter(
      c =>
        c &&
        typeof c.lat === "number" &&
        typeof c.lng === "number" &&
        !Number.isNaN(c.lat) &&
        !Number.isNaN(c.lng)
    )    

    if (validCrises.length === 0) return defaultCenter
      
      const avgLat = validCrises.reduce((sum, c) => sum + c.lat, 0) / validCrises.length
      const avgLng = validCrises.reduce((sum, c) => sum + c.lng, 0) / validCrises.length
      
      return [avgLat, avgLng]
    }

    const getMapZoom = (): number => {
      if (crises.length <= 1) return 3
      if (crises.length <= 3) return 2
      return 2
    }

    const mapCenter = getMapCenter()
    const mapZoom = getMapZoom()

    return (
      <div className="relative w-full overflow-hidden rounded-2xl" style={{ height: '520px' }}>
        {/* Radar overlay - renders on top of map */}
        <RadarOverlay isActive={isRadarActive} />
        
        {!isMapReady && (
          <div className="absolute inset-0 flex items-center justify-center bg-[#0d141f]">
            <div className="text-center">
              <div className="relative size-16 mx-auto mb-4">
                <div className="absolute inset-0 rounded-full border-4 border-cyan-400 border-t-transparent animate-spin"></div>
              </div>
              <p className="text-sm text-slate-400">Loading map...</p>
            </div>
          </div>
        )}
        <MapContainer
          center={mapCenter}
          zoom={mapZoom}
          className="h-full w-full"
          zoomControl={true}
          attributionControl={false}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
          dragging={true}
          whenReady={() => setIsMapReady(true)}
          
        >
          {/* Dark theme tile layer using CartoDB Dark Matter */}
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            subdomains="abcd"
            maxZoom={19}
          />
          
  <MapViewController 
    center={mapCenter} 
    zoom={mapZoom} 
    crises={crises}
    scanningCrisis={scanningCrisis}
  />
          
          {/* Render clustered markers */}
          {clusteredCrises.map((cluster, clusterIndex) => {
            const primaryCrisis = cluster.crises[0]
            const colors = colorMap[primaryCrisis.tone as keyof typeof colorMap] || colorMap.blue
            const isCluster = cluster.crises.length > 1
            
                  if (
          typeof cluster.lat !== "number" ||
          typeof cluster.lng !== "number" ||
          Number.isNaN(cluster.lat) ||
          Number.isNaN(cluster.lng)
        ) {
          return null
        }
            return (
              <Marker
                key={clusterIndex}
                position={[cluster.lat, cluster.lng]}
                icon={createCustomIcon(colors.color, colors.glowColor)}
                eventHandlers={{
                  click: () => {
                    // Select the first crisis in the cluster
                    onSelectCrisis(crises.indexOf(primaryCrisis))
                  },
                }}
              >
                <Popup>
    <div
      style={{
        background: `linear-gradient(
          135deg,
          ${colors.color}55,
          #101925 70%
        )`,
        border: `1px solid ${colors.color}`,
        borderRadius: "16px",
        padding: "16px",
        minWidth: "260px",
        color: "white",
        boxShadow: `0 0 30px ${colors.glowColor}`,
        fontFamily: "system-ui, sans-serif",
      }}
    >

      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "10px",
          marginBottom: "12px",
        }}
      >
        <div
          style={{
            width: "12px",
            height: "12px",
            borderRadius: "50%",
            background: colors.color,
            boxShadow: `0 0 15px ${colors.color}`,
          }}
        />

        <h3
          style={{
            margin: 0,
            fontSize: "16px",
            fontWeight: 700,
          }}
        >
          {primaryCrisis.title}
        </h3>
      </div>


      {/* Location */}
      <p
        style={{
          margin: "0 0 12px",
          color:"#cbd5e1",
          fontSize:"13px"
        }}
      >
        📍 {primaryCrisis.place}
      </p>


      {/* Danger meter */}
      <div
        style={{
          background:"rgba(0,0,0,0.25)",
          borderRadius:"12px",
          padding:"10px",
          marginBottom:"12px"
        }}
      >

        <div
          style={{
            display:"flex",
            justifyContent:"space-between",
            fontSize:"12px",
            marginBottom:"8px"
          }}
        >
          <span>
            Threat Level
          </span>

          <span
            style={{
              color:colors.color,
              fontWeight:700,
              textTransform:"uppercase"
            }}
          >
            {primaryCrisis.severity}
          </span>
        </div>


        <div
          style={{
            height:"8px",
            background:"#1e293b",
            borderRadius:"20px",
            overflow:"hidden"
          }}
        >
          <div
            style={{
              width:
                primaryCrisis.severity.toLowerCase().includes("critical")
                ? "95%"
                : primaryCrisis.severity.toLowerCase().includes("high")
                ? "75%"
                : "45%",
              height:"100%",
              background:colors.color,
              boxShadow:`0 0 15px ${colors.color}`
            }}
          />
        </div>

      </div>


      {/* Time */}
      <div
        style={{
          display:"flex",
          justifyContent:"space-between",
          fontSize:"12px",
          color:"#94a3b8"
        }}
      >
        <span>
          {primaryCrisis.time}
        </span>

        <span
          style={{
            color:colors.color,
            fontWeight:600
          }}
        >
          LIVE
        </span>
      </div>


    </div>
  </Popup>
              </Marker>
            )
          })}
        </MapContainer>
        
        {/* Radar overlay is now handled by RadarOverlay component above */}
        
        {/* Map overlay UI */}
        <div className="absolute left-5 top-5 sm:left-7 sm:top-7 z-[1000] pointer-events-none">
          <div className="pointer-events-auto">
            <div className="inline-flex items-center rounded-md border border-cyan-300/15 bg-cyan-400/[0.09] px-2 py-1">
              <span className="flex items-center gap-1.5 text-[10px] font-semibold uppercase tracking-[0.1em] text-cyan-300">
                <span className="relative flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-cyan-400 opacity-75"></span>
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-cyan-500"></span>
                </span>
                Live operational view
              </span>
            </div>
            <h2 className="mt-4 text-2xl font-semibold tracking-tight text-slate-100 sm:text-3xl">
              Global intelligence map
            </h2>
            <p className="mt-2 text-sm text-slate-400">
              Monitoring {crises.length} active sources across {new Set(crises.map(c => c.place)).size} regions
            </p>
          </div>
        </div>
        
        {/* Legend */}
        <div className="absolute bottom-4 left-4 z-[1000]">
          <div className="rounded-xl border border-white/[0.08] bg-[#0b111b]/85 px-3 py-2 backdrop-blur">
            <div className="flex items-center gap-3 text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-rose-400"></span>
                Critical
              </span>
              <span className="flex items-center gap-1.5">
                <span className="h-1.5 w-1.5 rounded-full bg-amber-300"></span>
                Elevated
              </span>
              <span className="hidden items-center gap-1.5 sm:flex">
                <span className="h-1.5 w-1.5 rounded-full bg-cyan-300"></span>
                Intelligence
              </span>
            </div>
          </div>
        </div>
      </div>
    )
  }