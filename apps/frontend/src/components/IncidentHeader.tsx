import { type ReactNode } from 'react'
import { Shield, MapPin, AlertTriangle, Activity, Radio } from 'lucide-react'
import { Panel } from '@/components/ui/panel'
import { StatusPill } from '@/components/ui/status-pill'

interface IncidentHeaderProps {
  title: string
  location: string
  severity: 'low' | 'moderate' | 'high' | 'critical'
  confidence: number
  status: string
  category: string
}

export function IncidentHeader({ title, location, severity, confidence, status, category }: IncidentHeaderProps) {
  const severityConfig = {
    critical: { tone: 'rose' as const, label: 'CRITICAL' },
    high: { tone: 'amber' as const, label: 'HIGH' },
    moderate: { tone: 'blue' as const, label: 'MODERATE' },
    low: { tone: 'emerald' as const, label: 'LOW' },
  }

  const config = severityConfig[severity] || severityConfig.moderate

  return (
    <Panel className="relative overflow-hidden p-6">
      {/* Background glow effect */}
      <div className="absolute -right-20 -top-20 size-64 rounded-full bg-cyan-400/[0.07] blur-3xl" />
      <div className="absolute -left-20 -bottom-20 size-48 rounded-full bg-blue-400/[0.05] blur-3xl" />

      <div className="relative">
        {/* Top row: Badge and Status */}
        <div className="flex flex-wrap items-center gap-3">
          <StatusPill tone="rose">
            <span className="flex items-center gap-1.5">
              <Radio className="size-3 animate-pulse" />
              Active Investigation
            </span>
          </StatusPill>
          <StatusPill tone={config.tone}>{config.label}</StatusPill>
          <StatusPill tone="cyan">
            <span className="flex items-center gap-1.5">
              <Activity className="size-3" />
              {status}
            </span>
          </StatusPill>
        </div>

        {/* Main title */}
        <h1 className="mt-4 text-2xl font-semibold tracking-tight text-slate-100 sm:text-3xl lg:text-4xl">
          {title}
        </h1>

        {/* Location and metadata */}
        <div className="mt-4 flex flex-wrap items-center gap-6 text-sm">
          <div className="flex items-center gap-2 text-slate-400">
            <MapPin className="size-4 text-cyan-300" />
            <span className="font-medium">{location}</span>
          </div>

          <div className="flex items-center gap-2 text-slate-400">
            <Shield className="size-4 text-violet-300" />
            <span className="text-xs uppercase tracking-wider">{category}</span>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500">Confidence:</span>
            <div className="flex items-center gap-2">
              <div className="h-1.5 w-24 overflow-hidden rounded-full bg-white/[0.08]">
                <div
                  className="h-full rounded-full bg-cyan-400"
                  style={{ width: `${confidence}%` }}
                />
              </div>
              <span className="text-sm font-semibold text-cyan-300">{confidence}%</span>
            </div>
          </div>
        </div>
      </div>
    </Panel>
  )
}