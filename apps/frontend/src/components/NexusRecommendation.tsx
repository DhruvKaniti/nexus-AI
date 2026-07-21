import { BrainCircuit, ArrowRight, CheckCircle2, AlertTriangle, Shield, Zap } from 'lucide-react'
import { Panel } from '@/components/ui/panel'
import { StatusPill } from '@/components/ui/status-pill'

interface NexusResponseProps {
  responsePriority: string
  responseActions: string[]
  responseConfidence: number
  eventCategory: string
  eventTitle: string
}

export function NexusResponse({ 
  responsePriority, 
  responseActions, 
  responseConfidence, 
  eventCategory,
  eventTitle 
}: NexusResponseProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return 'red'
      case 'HIGH':
        return 'amber'
      case 'MODERATE':
        return 'blue'
      case 'LOW':
        return 'emerald'
      default:
        return 'slate'
    }
  }

  const getPriorityBg = (priority: string) => {
    switch (priority) {
      case 'CRITICAL':
        return 'bg-red-400/[0.1]'
      case 'HIGH':
        return 'bg-amber-400/[0.1]'
      case 'MODERATE':
        return 'bg-blue-400/[0.1]'
      case 'LOW':
        return 'bg-emerald-400/[0.1]'
      default:
        return 'bg-slate-400/[0.1]'
    }
  }

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'cyber':
        return 'Cyber Response'
      case 'natural_disaster':
        return 'Disaster Response'
      case 'infrastructure':
        return 'Infrastructure Response'
      case 'geopolitical':
        return 'Security Response'
      case 'health':
        return 'Health Response'
      case 'economic':
        return 'Economic Response'
      default:
        return 'Operational Response'
    }
  }

  return (
    <Panel className="relative overflow-hidden p-6">
      {/* Background glow effects */}
      <div className="absolute -right-20 -top-20 size-64 rounded-full bg-cyan-400/[0.08] blur-3xl" />
      <div className="absolute -left-20 -bottom-20 size-48 rounded-full bg-blue-400/[0.05] blur-3xl" />

      <div className="relative">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-lg bg-cyan-400/[0.12] text-cyan-300">
              <BrainCircuit size={22} />
            </div>
            <div>
              <h2 className="text-sm font-semibold tracking-tight text-slate-100">Nexus Response Agent</h2>
              <p className="mt-0.5 text-[10px] text-slate-500">Intelligence-driven operational response</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <StatusPill tone={getPriorityColor(responsePriority) as any}>
              <span className="flex items-center gap-1.5">
                <Shield className="size-3" />
                {responsePriority}
              </span>
            </StatusPill>
            <StatusPill tone="emerald">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 className="size-3" />
                {responseConfidence}% Confidence
              </span>
            </StatusPill>
          </div>
        </div>

        {/* Response Category & Event */}
        <div className="mt-4 rounded-xl border border-white/[0.08] bg-white/[0.02] p-4">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="size-3 text-amber-400" />
            <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-amber-300">
              {getCategoryLabel(eventCategory)}
            </span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">{eventTitle}</p>
        </div>

        {/* Response Actions */}
        <div className="mt-4 rounded-xl border border-cyan-300/[0.15] bg-cyan-400/[0.05] p-5">
          <div className="flex gap-3">
            <AlertTriangle className="size-5 shrink-0 text-amber-300" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-slate-100">Recommended Response Actions</h3>
              <div className="mt-3 space-y-2.5">
                {responseActions.map((action, index) => (
                  <div key={index} className="flex items-start gap-2.5">
                    <span className="flex size-5 shrink-0 items-center justify-center rounded-md bg-cyan-400/[0.15] text-[10px] font-bold text-cyan-200">
                      {index + 1}
                    </span>
                    <p className="text-xs leading-relaxed text-slate-300 flex-1">{action}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Action buttons */}
        <div className="mt-5 flex items-center gap-3">
          <button className="flex flex-1 items-center justify-center gap-2 rounded-lg border border-cyan-300/20 bg-cyan-400/[0.08] px-4 py-2.5 text-xs font-medium text-cyan-300 transition-colors hover:bg-cyan-400/[0.12]">
            Execute Response Plan
            <ArrowRight size={14} />
          </button>
          <button className="flex items-center justify-center gap-2 rounded-lg border border-white/[0.09] bg-white/[0.025] px-4 py-2.5 text-xs text-slate-300 transition-colors hover:bg-white/[0.06]">
            Export Brief
          </button>
        </div>
      </div>
    </Panel>
  )
}
