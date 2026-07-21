import { Clock, Shield, Zap } from 'lucide-react'
import { Panel } from '@/components/ui/panel'
import { StatusPill } from '@/components/ui/status-pill'

interface SituationOverviewProps {
  summary: string
  impacts: string[]
  impactWindow: string
  riskCategories: string[]
}

export function SituationOverview({ summary, impacts, impactWindow, riskCategories }: SituationOverviewProps) {
  return (
    <Panel className="p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold tracking-tight text-slate-100">Situation Overview</h2>
        <StatusPill tone="amber">
          <span className="flex items-center gap-1.5">
            <Clock className="size-3" />
            {impactWindow}
          </span>
        </StatusPill>
      </div>

      <p className="mt-3 text-sm leading-relaxed text-slate-300">{summary}</p>

      <div className="mt-4">
        <h3 className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">Key Impacts</h3>
        <div className="mt-2 flex flex-wrap gap-2">
          {impacts.map((impact, index) => (
            <span
              key={index}
              className="inline-flex items-center gap-1.5 rounded-lg border border-white/[0.08] bg-white/[0.03] px-2.5 py-1.5 text-xs text-slate-300"
            >
              <Zap className="size-3 text-amber-300" />
              {impact}
            </span>
          ))}
        </div>
      </div>

      <div className="mt-4">
        <h3 className="text-[10px] font-semibold uppercase tracking-[0.16em] text-slate-500">Risk Categories</h3>
        <div className="mt-2 flex flex-wrap gap-2">
          {riskCategories.map((category, index) => (
            <StatusPill key={index} tone="violet">
              <span className="flex items-center gap-1.5">
                <Shield className="size-3" />
                {category}
              </span>
            </StatusPill>
          ))}
        </div>
      </div>
    </Panel>
  )
}