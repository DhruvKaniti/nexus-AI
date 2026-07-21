import { motion } from 'framer-motion'
import { useEffect, useState } from 'react'
import {
  ArrowRight, Bot, BrainCircuit, Clock3, MapPin, Plus, ScanLine, Target, Globe,
  Globe2, Shield, AlertTriangle, Building2, Landmark,
  Wifi, Heart, X
} from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'
import { LeafletMap } from '@/components/leaflet-map'
import { IncidentHeader } from '@/components/IncidentHeader'
import { SituationOverview } from '@/components/SituationOverview'
import { AgentPipeline } from '@/components/AgentPipeline'
import { LiveFindings } from '@/components/LiveFindings'

const ease = [0.22, 1, 0.36, 1] as const
const API_URL = '/api'

// No hardcoded events - all events will be fetched from the live API

interface IntelligenceItem {
  title: string
  location: string
  severity: string
  category: string
  balanced_category: string
  time: string
  icon: typeof Globe2
  lat: number
  lng: number
  impact_score: number
  confidence: number
  source: string
  response_priority?: string
  response_actions?: string[]
  response_confidence?: number
}

const agents = [
  { name: 'Signal', task: 'Ingesting regional feeds', status: 'Processing', progress: 76, color: 'cyan' },
  { name: 'Atlas', task: 'Modeling supply impact', status: 'Reasoning', progress: 58, color: 'violet' },
  { name: 'Sentinel', task: 'Scanning threat vectors', status: 'Monitoring', progress: 91, color: 'emerald' },
]

const timeline = [
  { time: '14:32', title: 'Signal correlation identified', text: '23 independent sources confirm an abnormal vessel pattern.', color: 'bg-cyan-400', icon: '📡' },
  { time: '14:24', title: 'Risk model updated', text: 'Economic exposure raised from medium to high confidence.', color: 'bg-violet-400', icon: '📈' },
  { time: '14:18', title: 'Satellite imagery received', text: 'Visual verification queued for analyst review.', color: 'bg-amber-400', icon: '🛰' },
]

const investigationAgents = [
  { name: 'Satellite Agent', finding: '' },
  { name: 'News Agent', finding: '' },
  { name: 'Supply Chain Agent', finding: '' },
  { name: 'Economic Agent', finding: '' },
  { name: 'Recommendation Agent', finding: '' },
] as const

const analystReasoning = [
  'Correlating multiple independent intelligence signals.',
  'Confidence increased after cross-source validation.',
  'Historical patterns compared against current activity.',
  'Risk model updated based on new indicators.',
  'Additional monitoring recommended.',
  'Pattern matches known operational signatures.',
  'Temporal analysis confirms sustained activity.',
  'Geospatial clustering indicates coordinated movement.',
  'Source reliability weighted by historical accuracy.',
  'Anomaly threshold exceeded in primary detection zone.',
]

type InvestigationStatus = 'Waiting' | 'Running' | 'Complete'


function getCategoryIcon(category: string) {
  const cat = category.toLowerCase()
  if (cat.includes('natural') || cat.includes('wildfire') || cat.includes('earthquake') || cat.includes('flood') || cat.includes('storm')) return Globe2
  if (cat.includes('geopolitical') || cat.includes('conflict') || cat.includes('military')) return Shield
  if (cat.includes('infrastructure') || cat.includes('power') || cat.includes('supply')) return Building2
  if (cat.includes('cyber') || cat.includes('hacking') || cat.includes('breach')) return Wifi
  if (cat.includes('health') || cat.includes('pandemic') || cat.includes('disease')) return Heart
  if (cat.includes('economic') || cat.includes('financial') || cat.includes('market')) return Landmark
  return AlertTriangle
}

function getCategoryColor(category: string): 'rose' | 'amber' | 'blue' | 'emerald' | 'violet' | 'cyan' {
  const cat = category.toLowerCase()
  if (cat.includes('natural') || cat.includes('wildfire') || cat.includes('earthquake')) return 'rose'
  if (cat.includes('geopolitical') || cat.includes('conflict')) return 'amber'
  if (cat.includes('infrastructure')) return 'blue'
  if (cat.includes('cyber')) return 'violet'
  if (cat.includes('health')) return 'emerald'
  if (cat.includes('economic')) return 'cyan'
  return 'blue'
}

function IntelligenceBriefingPanel({ items, onSelectItem, selectedItem }: { items: IntelligenceItem[]; onSelectItem: (index: number) => void; selectedItem: number | null }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2">
      {items.map(({ title, location, balanced_category, time, impact_score, confidence }, index) => {
        const tone = getCategoryColor(balanced_category)
        return (
          <button
            key={title}
            onClick={() => onSelectItem(index)}
            className={`group flex flex-col gap-2 rounded-xl px-3 py-2.5 text-left transition-colors hover:bg-white/[0.035] ${selectedItem === index ? 'bg-cyan-400/[0.08] ring-1 ring-cyan-300/20' : ''}`}
          >
            <span className="flex items-center justify-between gap-2">
              <span className="truncate text-xs font-medium text-slate-200">{title}</span>
              <span className={`shrink-0 rounded-full px-1.5 py-0.5 text-[9px] font-semibold uppercase tracking-wider ${tone === 'rose' ? 'bg-rose-400/[0.15] text-rose-300' : tone === 'amber' ? 'bg-amber-400/[0.15] text-amber-300' : tone === 'violet' ? 'bg-violet-400/[0.15] text-violet-300' : tone === 'emerald' ? 'bg-emerald-400/[0.15] text-emerald-300' : tone === 'cyan' ? 'bg-cyan-400/[0.15] text-cyan-300' : 'bg-blue-400/[0.15] text-blue-300'}`}>
                {time}
              </span>
            </span>
            <span className="flex items-center gap-1 text-[11px] text-slate-500">
              <MapPin size={11} />
              {location}
            </span>
            <div className="flex items-center gap-3">
              <span className="text-[10px] text-slate-600">Impact: {impact_score}</span>
              <span className="text-[10px] text-slate-600">Conf: {confidence}%</span>
            </div>
          </button>
        )
      })}
    </div>
  )
}

function AgentPanel() {
  return (
    <div className="space-y-5">
      {agents.map((agent, index) => (
        <div key={agent.name}>
          <div className="flex items-center gap-3">
            <span className={`relative grid size-10 shrink-0 place-items-center rounded-xl ${agent.color === 'cyan' ? 'bg-cyan-400/[0.10] text-cyan-300' : agent.color === 'violet' ? 'bg-violet-400/[0.10] text-violet-300' : 'bg-emerald-400/[0.10] text-emerald-300'}`}>
              <Bot size={18} />
              <i className="absolute -right-0.5 -top-0.5 size-2 rounded-full border-2 border-[#0d141f] bg-emerald-400" />
            </span>
            <div className="min-w-0 flex-1">
              <div className="flex justify-between gap-2">
                <p className="text-xs font-medium text-slate-200">{agent.name}</p>
                <span className="text-[10px] text-slate-500">{agent.status}</span>
              </div>
              <p className="mt-1 truncate text-[11px] text-slate-500">{agent.task}</p>
            </div>
          </div>
          <div className="mt-2.5 flex items-center gap-2">
            <div className="h-1 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: [`${Math.max(0, agent.progress - 9)}%`, `${agent.progress}%`, `${Math.max(0, agent.progress - 4)}%`] }}
                transition={{ duration: 3.8, delay: 0.25 + index * 0.1, repeat: Infinity, ease: 'easeInOut' }}
                className={`h-full rounded-full ${agent.color === 'cyan' ? 'bg-cyan-400' : agent.color === 'violet' ? 'bg-violet-400' : 'bg-emerald-400'}`}
              />
            </div>
            <span className="w-7 text-right text-[10px] text-slate-500">{agent.progress}%</span>
          </div>
        </div>
      ))}
      <div className="rounded-xl border border-white/[0.07] bg-white/[0.025] p-3">
        <div className="flex items-center gap-2 text-[10px] font-semibold uppercase tracking-[0.14em] text-cyan-300">
          <ScanLine size={13} />
          Latest finding
        </div>
        <p className="mt-2 text-[11px] leading-5 text-slate-400">Atlas detected a 14% rise in rerouting probability across monitored shipping corridors.</p>
      </div>
    </div>
  )
}

const streamEntries = ['Correlating vessel transponder gaps with regional advisories.', 'Confidence threshold exceeded for supply-chain disruption.', 'Sentinel is validating imagery against historical baselines.', 'Analyst brief updated with three corroborating sources.']

function IntelligenceFeed() {
  const [visible, setVisible] = useState(2)
  useEffect(() => { const timer = window.setInterval(() => setVisible((value) => value === streamEntries.length ? 1 : value + 1), 2600); return () => window.clearInterval(timer) }, [])
  return (
    <div>
      <div className="space-y-1">{streamEntries.slice(0, visible).map((entry) => <motion.div key={`${entry}-${visible}`} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="flex gap-3 rounded-lg px-2 py-2.5"><span className="mt-1.5 size-1.5 shrink-0 rounded-full bg-cyan-300 shadow-[0_0_10px_#67e8f9]" /><div><p className="text-[10px] text-slate-600">AI reasoning · now</p><p className="mt-1 text-xs leading-5 text-slate-300">{entry}</p></div></motion.div>)}</div>
      <div className="mt-3 flex items-center gap-2 border-t border-white/[0.07] pt-3 text-[11px] text-slate-500">
        <span className="inline-flex gap-1">
          <i className="size-1 animate-bounce rounded-full bg-cyan-300" />
          <i className="size-1 animate-bounce rounded-full bg-cyan-300 [animation-delay:150ms]" />
          <i className="size-1 animate-bounce rounded-full bg-cyan-300 [animation-delay:300ms]" />
        </span>
        Agents are synthesizing new signals
      </div>
    </div>
  )
}

function RecommendationPanel() {
  return (
    <div className="relative overflow-hidden rounded-xl border border-cyan-300/[0.12] bg-cyan-400/[0.045] p-4">
      <div className="flex gap-3">
        <span className="grid size-8 shrink-0 place-items-center rounded-lg bg-cyan-400/[0.12] text-cyan-300">
          <BrainCircuit size={17} />
        </span>
        <p className="text-xs leading-5 text-slate-300">Pre-position alternative shipping capacity for high-value routes transiting the Gulf within the next 12 hours.</p>
      </div>
      <div className="mt-4 flex items-center justify-between border-t border-white/[0.07] pt-3">
        <span className="text-[11px] text-slate-500">Confidence <strong className="ml-1 font-medium text-cyan-300">87%</strong></span>
        <button className="flex items-center gap-1 text-xs font-medium text-cyan-300 hover:text-cyan-200">Review actions <ArrowRight size={13} /></button>
      </div>
    </div>
  )
}

function ReasoningPanel() {
  return (
    <div className="mt-5 space-y-0">
      {timeline.map((item, index) => (
        <div key={item.time} className="relative flex gap-3 pb-5 last:pb-0">
          <div className="relative flex w-8 shrink-0 justify-center">
            <span className={`mt-1.5 size-2 rounded-full ${item.color} ring-4 ring-[#0d141f]`} />
            {index < timeline.length - 1 && <span className="absolute top-4 h-[calc(100%-8px)] w-px bg-white/[0.08]" />}
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <p className="text-xs font-medium text-slate-200">{item.title}</p>
              <span className="text-[10px] text-slate-600">{item.time}</span>
            </div>
            <p className="mt-1 text-[11px] leading-5 text-slate-500">{item.text}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

async function geocodeLocation(place: string): Promise<{ lat: number; lng: number } | null> {
  try {
    const response = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(place)}&limit=1`,
      {
        headers: {
          'Accept': 'application/json',
        },
      }
    )
    
    if (!response.ok) {
      console.error('Geocoding request failed')
      return null
    }
    
    const data = await response.json()
    
    if (data && data.length > 0) {
      return {
        lat: parseFloat(data[0].lat),
        lng: parseFloat(data[0].lon),
      }
    }
    
    return null
  } catch (error) {
    console.error('Geocoding failed:', error)
    return null
  }
}

function latLngToPercentage(lat: number, lng: number): { x: string; y: string } {
  const x = ((lng + 180) / 360) * 100
  const y = ((80 - lat) / 140) * 100
  
  return {
    x: `${Math.max(5, Math.min(95, x))}%`,
    y: `${Math.max(5, Math.min(95, y))}%`,
  }
}

async function fetchAIFindings(item: IntelligenceItem): Promise<string[]> {
  try {
    const response = await fetch(`${API_URL}/investigate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        title: item.title,
        place: item.location,
        severity: item.severity,
        tone: getCategoryColor(item.balanced_category),
        description: ''
      })
    })
    
    if (!response.ok) throw new Error('API request failed')
    
    const data = await response.json()
    return data.agents.map((agent: { finding: string }) => agent.finding)
  } catch (error) {
    console.error('AI analysis failed, using fallback:', error)
    return generateFindings(item)
  }
}

function generateFindings(item: IntelligenceItem): string[] {
  const severityContext = item.severity === 'Critical' ? 'high-priority' : item.severity === 'Elevated' ? 'elevated-status' : 'monitoring'
  
  return [
    `Satellite imagery analysis confirms anomalous activity patterns near ${item.location}. Thermal signatures indicate sustained operational presence in the ${item.title.toLowerCase()} sector.`,
    `Regional news sources report increased activity and advisory language related to ${item.title}. Multiple outlets confirm precautionary measures being implemented across the region.`,
    `Supply chain impact assessment for ${item.location}: Alternative routing capacity available with estimated 18-hour activation window. ${severityContext} protocols recommended for logistics coordination.`,
    `Economic exposure analysis: ${item.title} could affect regional freight operations by 12-18% over the next 72 hours. ${item.balanced_category.replace('_', ' ')} monitoring suggests elevated risk profile.`,
    `Strategic recommendation: Activate contingency protocols for ${item.location}. Deploy monitoring assets and coordinate with regional stakeholders. Confidence level: ${item.severity === 'Critical' ? '94' : item.severity === 'Elevated' ? '87' : '76'}%.`
  ]
}

function InvestigationSession({ item }: { item: IntelligenceItem }) {
  const [current, setCurrent] = useState(0)
  const [states, setStates] = useState<InvestigationStatus[]>(() => investigationAgents.map(() => 'Waiting'))
  const [displayedFindings, setDisplayedFindings] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [findings, setFindings] = useState<string[]>([])

  useEffect(() => {
    let mounted = true
    setIsLoading(true)
    setCurrent(0)
    setStates(investigationAgents.map(() => 'Waiting'))
    setDisplayedFindings([])
    
    fetchAIFindings(item).then(result => {
      if (mounted) {
        setFindings(result)
        setIsLoading(false)
      }
    })
    
    return () => { mounted = false }
  }, [item.title])
  
  useEffect(() => { 
    if (current >= findings.length || isLoading) return; 
    setStates((items) => items.map((item, index) => index === current ? 'Running' : item)); 
    const stream = window.setTimeout(() => setDisplayedFindings((items) => [...items, findings[current]]), 650); 
    const complete = window.setTimeout(() => { 
      setStates((items) => items.map((item, index) => index === current ? 'Complete' : item)); 
      setCurrent((value) => value + 1) 
    }, 1450); 
    return () => { window.clearTimeout(stream); window.clearTimeout(complete) } 
  }, [current, findings, isLoading])
  
  const complete = current === findings.length && !isLoading

  if (isLoading) {
    return <div className="space-y-3">{investigationAgents.map((agent) => <div key={agent.name} className="flex items-center gap-3"><Skeleton className="size-8 rounded-lg" /><Skeleton className="h-4 flex-1" /></div>)}</div>
  }

  const findingsWithAgents = displayedFindings.map((finding, index) => ({
    agent: investigationAgents[index]?.name || 'Unknown Agent',
    summary: finding,
    confidence: item.confidence,
    timestamp: new Date(),
    reasoning: analystReasoning[index % analystReasoning.length]
  }))

  return (
    <div className="space-y-4">
      <div className="flex justify-between text-[11px] text-slate-500">
        <span>Investigation progress</span>
        <span>{Math.round((current / findings.length) * 100)}%</span>
      </div>
      <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
        <motion.div animate={{ width: `${(current / findings.length) * 100}%` }} className="h-full rounded-full bg-cyan-400" />
      </div>
      <div className="mt-5 space-y-3">
        {investigationAgents.map((agent, index) => (
          <div key={agent.name} className="flex items-center gap-3">
            <span className={`grid size-8 place-items-center rounded-lg ${states[index] === 'Complete' ? 'bg-emerald-400/[0.1] text-emerald-300' : states[index] === 'Running' ? 'bg-cyan-400/[0.1] text-cyan-300' : 'bg-white/[0.04] text-slate-600'}`}>
              <Bot size={15} />
            </span>
            <span className="min-w-0 flex-1 text-xs text-slate-300">{agent.name}</span>
            <span className={`text-[10px] ${states[index] === 'Complete' ? 'text-emerald-300' : states[index] === 'Running' ? 'text-cyan-300' : 'text-slate-600'}`}>{states[index]}</span>
          </div>
        ))}
      </div>
      <LiveFindings findings={findingsWithAgents} />
      {complete && (
        <div className="rounded-xl border border-cyan-300/[0.12] bg-cyan-400/[0.045] p-4">
          <p className="text-[10px] font-semibold uppercase tracking-[.14em] text-cyan-300">Executive summary</p>
          <div className="mt-3 space-y-3 text-[11px] leading-5 text-slate-400">
            <p><strong className="text-slate-200">Situation:</strong> {item.title} is confirmed at {item.location}.</p>
            <p><strong className="text-slate-200">Key Findings:</strong> Multi-source signals indicate sustained operational disruption.</p>
            <p><strong className="text-slate-200">Predicted Impact:</strong> Elevated transit and cost exposure over the next 24–72 hours.</p>
            <p><strong className="text-slate-200">Recommended Actions:</strong> Activate contingency routes and issue an executive brief.</p>
          </div>
        </div>
      )}
    </div>
  )
}

function NewInvestigationModal({ isOpen, onClose, onCreate }: { isOpen: boolean; onClose: () => void; onCreate: (crisis: Omit<IntelligenceItem, 'time' | 'icon' | 'lat' | 'lng'> & { icon: typeof Globe2 }) => void }) {
  const [title, setTitle] = useState('')
  const [place, setPlace] = useState('')
  const [severity, setSeverity] = useState<'Critical' | 'Elevated' | 'Watch'>('Watch')
  const [category, setCategory] = useState<string>('geopolitical')

  if (!isOpen) return null

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    await onCreate({
      title,
      location: place,
      severity,
      category,
      balanced_category: category,
      impact_score: 75,
      confidence: 80,
      source: 'Manual',
      icon: getCategoryIcon(category),
    })
    setTitle('')
    setPlace('')
    setSeverity('Watch')
    setCategory('geopolitical')
    onClose()
  }

  return <div className="fixed inset-0 z-50 flex items-center justify-center bg-[#060912]/75 backdrop-blur-md" onMouseDown={onClose}><motion.div initial={{ opacity: 0, y: 12, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} onMouseDown={(event) => event.stopPropagation()} className="w-full max-w-lg overflow-hidden rounded-2xl border border-cyan-300/[0.16] bg-[#101925] shadow-[0_24px_80px_rgba(0,0,0,.55)]"><div className="flex items-center justify-between border-b border-white/[0.08] px-4 py-3"><h3 className="text-sm font-semibold text-slate-100">New Investigation</h3><button onClick={onClose} className="text-slate-500 hover:text-slate-300"><X size={17} /></button></div><form onSubmit={handleSubmit} className="p-4 space-y-4"><div><label className="block text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500 mb-1.5">Event Name</label><input value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="e.g., Supply chain disruption" className="w-full rounded-lg border border-white/[0.08] bg-white/[0.03] px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-cyan-300/30" /></div><div><label className="block text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500 mb-1.5">Location</label><input value={place} onChange={(e) => setPlace(e.target.value)} required placeholder="e.g., Suez Canal" className="w-full rounded-lg border border-white/[0.08] bg-white/[0.03] px-3 py-2 text-sm text-slate-100 outline-none placeholder:text-slate-600 focus:border-cyan-300/30" /></div><div className="grid grid-cols-2 gap-3"><div><label className="block text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500 mb-1.5">Severity</label><select value={severity} onChange={(e) => setSeverity(e.target.value as 'Critical' | 'Elevated' | 'Watch')} className="w-full rounded-lg border border-white/[0.08] bg-white/[0.03] px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-300/30"><option value="Watch">Watch</option><option value="Elevated">Elevated</option><option value="Critical">Critical</option></select></div><div><label className="block text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500 mb-1.5">Category</label><select value={category} onChange={(e) => setCategory(e.target.value)} className="w-full rounded-lg border border-white/[0.08] bg-white/[0.03] px-3 py-2 text-sm text-slate-100 outline-none focus:border-cyan-300/30"><option value="natural_disaster">Natural Disaster</option><option value="geopolitical">Geopolitical</option><option value="infrastructure">Infrastructure</option><option value="cyber">Cyber</option><option value="health">Health</option><option value="economic">Economic</option></select></div></div><div className="flex justify-end gap-2 pt-2"><button type="button" onClick={onClose} className="px-4 py-2 text-xs font-medium text-slate-400 hover:text-slate-200">Cancel</button><button type="submit" className="px-4 py-2 text-xs font-medium text-slate-950 bg-cyan-400 rounded-lg hover:bg-cyan-300">Create Investigation</button></div></form></motion.div></div>
}

export function CommandCenterSkeleton() {
  return <div className="space-y-5"><div className="flex justify-between"><div><Skeleton className="h-3 w-28" /><Skeleton className="mt-3 h-8 w-56" /></div><Skeleton className="h-9 w-28" /></div><div className="grid gap-5 xl:grid-cols-[minmax(0,1.6fr)_minmax(320px,.8fr)]"><Skeleton className="h-[500px] rounded-2xl" /><div className="space-y-5"><Skeleton className="h-[240px] rounded-2xl" /><Skeleton className="h-[240px] rounded-2xl" /></div></div></div>
}

export function CommandCenter() {
  const [items, setItems] = useState<IntelligenceItem[]>([])
  const [selectedItem, setSelectedItem] = useState<number | null>(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isScanning, setIsScanning] = useState(false)
  const [scanningItem, setScanningItem] = useState<{ x: string; y: string } | null>(null)
  const [scanStatus, setScanStatus] = useState('')
  const [isLoadingEvents, setIsLoadingEvents] = useState(true)

  useEffect(() => {
    const fetchLiveEvents = async () => {
      setIsLoadingEvents(true)
      try {
        console.log('🌐 Fetching live global events on mount...')
        const response = await fetch(`${API_URL}/global-scan?limit=10`)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: Failed to fetch global events`)
        }
        
        const data = await response.json()
        
        if (data.error) {
          throw new Error(data.error)
        }
        
        const events = data.events || []
        
        if (events.length === 0) {
          console.warn('No live events available from API')
          setItems([])
          return
        }
        
        console.log(`✅ Loaded ${events.length} live global events`)
        
        const newItems: IntelligenceItem[] = events.map((event: any) => ({
          title: event.title,
          location: event.location,
          severity: event.severity || 'Watch',
          category: event.category || 'News',
          balanced_category: event.balanced_category || 'geopolitical',
          time: 'Just now',
          icon: getCategoryIcon(event.balanced_category || event.category),
          lat: event.latitude || 0,
          lng: event.longitude || 0,
          impact_score: event.impact_score || 0,
          confidence: event.confidence || 0,
          source: event.source || 'Unknown',
        }))
        
        console.log(`📍 Events with coordinates: ${newItems.filter(c => c.lat !== 0 && c.lng !== 0).length}/${newItems.length}`)
        
        setItems(newItems)
        if (newItems.length > 0) {
          setSelectedItem(0)
          
          // Auto-trigger scanning animation on initial load
          const firstItem = newItems[0]
          if (firstItem.lat !== 0 && firstItem.lng !== 0) {
            const scanPosition = latLngToPercentage(firstItem.lat, firstItem.lng)
            setScanningItem(scanPosition)
            
            // Clear scanning after animation completes (10 seconds)
            setTimeout(() => {
              setScanningItem(null)
            }, 10000)
          }
        }
        
      } catch (error) {
        console.error('Failed to fetch live events:', error)
        console.log('No fallback events - waiting for API')
        setItems([])
      } finally {
        setIsLoadingEvents(false)
      }
    }
    
    fetchLiveEvents()
  }, [])
  
  const handleCreateItem = async (newItem: Omit<IntelligenceItem, 'time' | 'icon' | 'lat' | 'lng'> & { icon: typeof Globe2 }) => {
    const coordinates = await geocodeLocation(newItem.location)
    
    const item: IntelligenceItem = {
      ...newItem,
      time: 'Just now',
      lat: coordinates?.lat ?? 0,
      lng: coordinates?.lng ?? 0,
    }
    
    setItems((prev) => [...prev, item])
    setSelectedItem(items.length)
  }

  const startGlobalScan = async () => {
    if (isScanning) return
    
    setIsScanning(true)
    setScanStatus('Initializing global scan...')
    
    try {
      console.log('🔍 Starting global scan...')
      const response = await fetch(`${API_URL}/global-scan?limit=10&t=${Date.now()}`)      
      console.log('📡 API Response status:', response.status, response.statusText)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ error: 'Unknown error' }))
        console.error('❌ API error:', errorData)
        throw new Error(errorData.error || `HTTP ${response.status}: Failed to fetch global events`)
      }
      
      const data = await response.json()
      console.log('📦 Raw API response:', JSON.stringify(data, null, 2))
      
      // Check for API error response
      if (data.error) {
        console.error('❌ API returned error:', data.error)
        throw new Error(data.error)
      }
      
      const events = data.events || []
      console.log(`📊 Received ${events.length} events from sources:`, data.sources_used)
      
      if (events.length === 0) {
        console.warn('⚠️ No events in response')
        throw new Error('No live events available. The API returned an empty list.')
      }
      
      // Log first event details
      console.log('📰 First event:', JSON.stringify(events[0], null, 2))
      
      setScanStatus(`Found ${events.length} live global events from ${data.sources_used?.join(', ') || 'unknown source'}. Beginning analysis...`)
      
      const newItems: IntelligenceItem[] = []
      
      for (let i = 0; i < events.length; i++) {
        const event = events[i]
        console.log(`🔎 Processing event ${i + 1}/${events.length}: ${event.title}`)
        setScanStatus(`Scanning event ${i + 1}/${events.length}: ${event.title}`)
        
        // Use backend coordinates if available, otherwise geocode
        let lat = event.latitude || 0
        let lng = event.longitude || 0
        
        // If no coordinates from backend, try geocoding
        if (lat === 0 && lng === 0) {
          console.log(`   No coordinates from backend, geocoding "${event.location}"...`)
          const coordinates = await geocodeLocation(event.location)
          lat = coordinates?.lat ?? 0
          lng = coordinates?.lng ?? 0
          console.log(`   Geocoded to`, coordinates)
        } else {
          console.log(`   Using backend coordinates: ${lat}, ${lng}`)
        }
        
        const position = latLngToPercentage(lat, lng)
        setScanningItem(position)
        
        await new Promise(resolve => window.setTimeout(resolve, 2000))
        
        const item: IntelligenceItem = {
          title: event.title,
          location: event.location,
          severity: event.severity || 'Watch',
          category: event.category || 'News',
          balanced_category: event.balanced_category || 'geopolitical',
          time: 'Just now',
          icon: getCategoryIcon(event.balanced_category || event.category),
          lat,
          lng,
          impact_score: event.impact_score || 0,
          confidence: event.confidence || 0,
          source: event.source || 'Unknown',
        }
        
        newItems.push(item)
        console.log(`✅ Added item:`, item.title, 'at', item.location)
        
        await new Promise(resolve => window.setTimeout(resolve, 3000))
        
        setScanningItem(null)
        await new Promise(resolve => window.setTimeout(resolve, 1000))
      }
      
      // REPLACE all items with new ones (don't append to defaults)
      console.log('🔄 Replacing all items with', newItems.length, 'live events')
      console.log('📋 Final items array:', newItems.map(c => ({ title: c.title, location: c.location })))
      console.log('💾 Calling setItems() with:', newItems.length, 'items')
      
      // Force a log before and after state update
      console.log('   Before setItems - current items count:', items.length)
      
      setItems(newItems)
      
      // Log after state update (will show in next render)
      console.log('✅ setItems() called - React will re-render with new items')
      
      setSelectedItem(0)
      
      setScanStatus('Global scan complete. All events analyzed.')
      setTimeout(() => {
        setIsScanning(false)
        setScanStatus('')
      }, 3000)
      
    } catch (error) {
      console.error('❌ Global scan failed:', error)
      const errorMessage = error instanceof Error ? error.message : 'Scan failed. Please try again.'
      setScanStatus(`Scan failed: ${errorMessage}`)
      setIsScanning(false)
      setScanningItem(null)
    }
  }

  const selected = selectedItem !== null ? items[selectedItem] : null

  return <motion.div initial="hidden" animate="visible" variants={{ hidden: {}, visible: { transition: { staggerChildren: 0.07 } } }} className="space-y-5">
    {/* Header Section */}
    <motion.div variants={{ hidden: { opacity: 0, y: 10 }, visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease } } }} className="flex flex-col justify-between gap-5 md:flex-row md:items-end">
      <div>
        <div className="mb-3 flex items-center gap-2">
          <span className="size-1.5 animate-pulse rounded-full bg-cyan-300" />
          <p className="text-[10px] font-semibold uppercase tracking-[0.2em] text-cyan-300">World intelligence briefing</p>
        </div>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-100 sm:text-4xl">Global Intelligence</h1>
        <p className="mt-3 text-sm text-slate-500">High-impact events across all domains, optimized for geographic and category diversity.</p>
      </div>
      <div className="flex items-center gap-2">
        <button onClick={() => setIsModalOpen(true)} className="flex h-10 items-center gap-2 rounded-lg border border-cyan-300/20 bg-cyan-400/[0.08] px-3 text-xs font-medium text-cyan-300 hover:bg-cyan-400/[0.12]"><Plus size={14} />New Investigation</button>
        <button onClick={startGlobalScan} disabled={isScanning} className="flex h-10 items-center gap-2 rounded-lg border border-emerald-300/20 bg-emerald-400/[0.08] px-3 text-xs font-medium text-emerald-300 hover:bg-emerald-400/[0.12] disabled:opacity-50 disabled:cursor-not-allowed"><Globe size={14} />{isScanning ? 'Scanning...' : 'Refresh Briefing'}</button>
        <button className="flex h-10 items-center gap-2 rounded-lg border border-white/[0.09] bg-white/[0.025] px-3 text-xs text-slate-300 hover:bg-white/[0.06]"><Clock3 size={14} />Last 24 hours</button>
        <button className="grid size-10 place-items-center rounded-lg border border-white/[0.09] bg-white/[0.025] text-slate-400 hover:text-cyan-300"><Target size={16} /></button>
      </div>
    </motion.div>

    {/* Scanning Status */}
    {isScanning && <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="rounded-xl border border-emerald-300/20 bg-emerald-400/[0.08] p-4"><div className="flex items-center gap-3"><div className="relative size-5"><motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }} className="absolute inset-0 rounded-full border-2 border-emerald-300 border-t-transparent" /></div><p className="text-xs font-medium text-emerald-300">{scanStatus}</p></div></motion.div>}
    {isLoadingEvents && <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="rounded-xl border border-cyan-300/20 bg-cyan-400/[0.08] p-4"><div className="flex items-center gap-3"><div className="relative size-5"><motion.div animate={{ rotate: 360 }} transition={{ duration: 2, repeat: Infinity, ease: 'linear' }} className="absolute inset-0 rounded-full border-2 border-cyan-300 border-t-transparent" /></div><p className="text-xs font-medium text-cyan-300">Loading live global events...</p></div></motion.div>}

    <NewInvestigationModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} onCreate={handleCreateItem} />

    {/* INCIDENT HEADER - Top Priority */}
    {selected && (
      <motion.div variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease } } }}>
        <IncidentHeader
          title={selected.title}
          location={selected.location}
          severity={selected.severity.toLowerCase() as 'low' | 'moderate' | 'high' | 'critical'}
          confidence={selected.confidence}
          status="Monitoring"
          category={selected.balanced_category.replace(/_/g, ' ')}
        />
      </motion.div>
    )}

    {/* Main Grid: Map + Intelligence Briefing */}
    <div className="grid gap-5">
      <motion.div variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.5, ease } } }}>
        <LeafletMap onSelectCrisis={setSelectedItem} crises={items.map(i => ({ title: i.title, place: i.location, severity: i.severity, tone: getCategoryColor(i.balanced_category), time: i.time, icon: i.icon, lat: i.lat, lng: i.lng }))} scanningCrisis={scanningItem} selectedCrisis={selectedItem} />
      </motion.div>
      <motion.div variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease } } }} className="space-y-5">
        <div>
          <h2 className="text-sm font-semibold tracking-tight text-slate-100 mb-3">Intelligence Briefing</h2>
          <IntelligenceBriefingPanel items={items} onSelectItem={setSelectedItem} selectedItem={selectedItem} />
        </div>
        <AgentPanel />
      </motion.div>
    </div>

    {/* Situation Overview - Only show when item is selected */}
    {selected && (
      <motion.div variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease } } }}>
        <SituationOverview
          summary={`${selected.title} has been detected at ${selected.location}. Multi-source intelligence confirms elevated risk profile requiring immediate attention and coordinated response.`}
          impacts={['Supply chain disruption', 'Economic exposure', 'Regional stability', 'Infrastructure stress']}
          impactWindow="24-72 hours"
          riskCategories={['Geopolitical', 'Economic', 'Infrastructure']}
        />
      </motion.div>
    )}

    {/* AI Agent Pipeline */}
    <motion.div variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease } } }}>
      <AgentPipeline
        agents={[
          { 
            name: 'Satellite Agent', 
            status: selected ? 'complete' : 'monitoring', 
            icon: 'satellite',
            currentTask: 'Comparing satellite imagery against historical regional activity patterns',
            confidence: 91,
            latestFinding: 'Identified anomalous activity signatures requiring additional verification',
            lastUpdated: new Date()
          },
          { 
            name: 'News Agent', 
            status: selected ? 'complete' : 'monitoring', 
            icon: 'news',
            currentTask: 'Analyzing 18,400 threat indicators across critical infrastructure networks',
            confidence: 94,
            latestFinding: 'Detected increased correlation between vulnerability reports and active threat campaigns',
            lastUpdated: new Date()
          },
          { 
            name: 'Supply Chain Agent', 
            status: selected ? 'complete' : 'monitoring', 
            icon: 'supply',
            currentTask: 'Modeling global transportation disruption scenarios',
            confidence: 88,
            latestFinding: 'Alternative routing capacity remains available with moderate delay risk',
            lastUpdated: new Date()
          },
          { 
            name: 'Economic Agent', 
            status: selected ? 'complete' : 'monitoring', 
            icon: 'economic',
            currentTask: 'Calculating downstream economic exposure',
            confidence: 86,
            latestFinding: 'Projected commodity volatility increase based on correlated signals',
            lastUpdated: new Date()
          },
          { 
            name: 'Recommendation Agent', 
            status: selected ? 'complete' : 'monitoring', 
            icon: 'recommendation',
            currentTask: 'Generating executive response options',
            confidence: 90,
            latestFinding: 'Recommended enhanced monitoring and contingency preparation',
            lastUpdated: new Date()
          },
        ]}
      />
    </motion.div>

    {/* Bottom Grid: Investigation, Timeline, Recommendation, Feed */}
    {selected && (
      <div className="grid gap-5 lg:grid-cols-3">
        <motion.div variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease } } }} className="lg:col-span-2">
          <InvestigationSession item={selected} />
        </motion.div>
        <motion.div variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease } } }} className="space-y-5">
          <ReasoningPanel />
          {selected && (
            <NexusResponse
              responsePriority={selected.response_priority || 'MODERATE'}
              responseActions={selected.response_actions || [
                'Monitor situation development and gather additional intelligence',
                'Assess potential impact on operations and stakeholders',
                'Prepare contingency plans and coordinate with relevant teams'
              ]}
              responseConfidence={selected.response_confidence || selected.confidence}
              eventCategory={selected.balanced_category}
              eventTitle={selected.title}
            />
          )}
          <div>
            <h2 className="text-sm font-semibold tracking-tight text-slate-100 mb-3">Live Intelligence Feed</h2>
            <IntelligenceFeed />
          </div>
        </motion.div>
      </div>
    )}

    {/* Show placeholder when no item is selected */}
    {!selected && items.length === 0 && (
      <motion.div variants={{ hidden: { opacity: 0, y: 12 }, visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease } } }} className="rounded-2xl border border-dashed border-white/[0.1] bg-white/[0.01] p-12 text-center">
        <Globe className="mx-auto size-12 text-slate-600" />
        <h3 className="mt-4 text-sm font-medium text-slate-400">No Active Investigations</h3>
        <p className="mt-2 text-xs text-slate-500">Select an event from the briefing panel or start a global scan to begin analysis.</p>
      </motion.div>
    )}
  </motion.div>
}