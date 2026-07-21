import { useState, useEffect } from 'react'
import { Satellite, Newspaper, Truck, TrendingUp, Bot, CheckCircle2, Shield } from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'
import { Panel } from '@/components/ui/panel'
import { StatusPill } from '@/components/ui/status-pill'

interface Finding {
  agent: string
  summary: string
  confidence?: number
  timestamp?: Date
  reasoning?: string
}

interface LiveFindingsProps {
  findings: Finding[]
}

const agentIcons: Record<string, { icon: typeof Satellite; color: string }> = {
  'Satellite Agent': { icon: Satellite, color: 'cyan' },
  'News Agent': { icon: Newspaper, color: 'blue' },
  'Supply Chain Agent': { icon: Truck, color: 'violet' },
  'Economic Agent': { icon: TrendingUp, color: 'emerald' },
  'Recommendation Agent': { icon: Bot, color: 'amber' },
}

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

export function LiveFindings({ findings }: LiveFindingsProps) {
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  }

  const getRandomReasoning = () => {
    return analystReasoning[Math.floor(Math.random() * analystReasoning.length)]
  }

  return (
    <Panel className="p-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold tracking-tight text-slate-100">Live Findings</h2>
          <p className="mt-1 text-[10px] text-slate-500">Real-time intelligence analysis stream</p>
        </div>
        <StatusPill tone="cyan">
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="size-3" />
            {findings.length} Intelligence Reports
          </span>
        </StatusPill>
      </div>

      <div className="mt-4 space-y-3">
        <AnimatePresence mode="popLayout">
          {findings.map((finding, index) => {
            const config = agentIcons[finding.agent] || { icon: Bot, color: 'slate' }
            const Icon = config.icon
            const reasoning = finding.reasoning || getRandomReasoning()

            return (
              <motion.div
                key={`${finding.agent}-${index}`}
                initial={{ opacity: 0, y: 10, scale: 0.98 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -10, scale: 0.98 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
                className="group relative overflow-hidden rounded-xl border border-white/[0.08] bg-white/[0.02] p-4 transition-all duration-300 hover:border-white/[0.15] hover:bg-white/[0.04]"
              >
                <div className="flex gap-3">
                  {/* Agent icon */}
                  <div className={`grid size-10 shrink-0 place-items-center rounded-lg ${config.color === 'cyan' ? 'bg-cyan-400/[0.1] text-cyan-300' : config.color === 'blue' ? 'bg-blue-400/[0.1] text-blue-300' : config.color === 'violet' ? 'bg-violet-400/[0.1] text-violet-300' : config.color === 'emerald' ? 'bg-emerald-400/[0.1] text-emerald-300' : 'bg-amber-400/[0.1] text-amber-300'}`}>
                    <Icon size={18} />
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="text-xs font-semibold text-slate-200">{finding.agent}</h3>
                      <div className="flex items-center gap-2 shrink-0">
                        {finding.confidence !== undefined && (
                          <span className="flex items-center gap-1 text-[10px] font-medium text-cyan-300">
                            <Shield className="size-3" />
                            {finding.confidence}%
                          </span>
                        )}
                        <span className="text-[9px] text-slate-600">
                          {formatTime(finding.timestamp || currentTime)}
                        </span>
                      </div>
                    </div>
                    
                    {/* Reasoning */}
                    <div className="mt-2 flex items-start gap-1.5 rounded-lg bg-white/[0.02] px-2.5 py-2 border border-white/[0.04]">
                      <span className="text-[10px] text-slate-500 italic leading-relaxed flex-1">
                        {reasoning}
                      </span>
                    </div>

                    <p className="mt-2.5 text-xs leading-relaxed text-slate-400">{finding.summary}</p>
                  </div>
                </div>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </Panel>
  )
}