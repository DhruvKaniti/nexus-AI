import { type ReactNode } from 'react'
import { Panel } from '@/components/ui/panel'
import { StatusPill } from '@/components/ui/status-pill'

interface TimelineEvent {
  time: string
  icon: ReactNode
  title: string
  explanation: string
  color: string
}

interface ReasoningTimelineProps {
  events: TimelineEvent[]
}

export function ReasoningTimeline({ events }: ReasoningTimelineProps) {
  return (
    <Panel className="p-5">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold tracking-tight text-slate-100">AI Reasoning Timeline</h2>
        <StatusPill tone="violet">
          <span className="flex items-center gap-1.5">
            <span className="size-1.5 animate-pulse rounded-full bg-violet-400" />
            Live Trace
          </span>
        </StatusPill>
      </div>

      <div className="mt-5 space-y-0">
        {events.map((event, index) => (
          <div key={index} className="relative flex gap-3 pb-5 last:pb-0">
            {/* Timeline line and dot */}
            <div className="relative flex w-8 shrink-0 justify-center">
              <span className={`mt-1.5 size-2 rounded-full ${event.color} ring-4 ring-[#0d141f]`} />
              {index < events.length - 1 && (
                <span className="absolute top-4 h-[calc(100%-8px)] w-px bg-white/[0.08]" />
              )}
            </div>

            {/* Event content */}
            <div className="min-w-0 flex-1">
              <div className="flex items-center gap-2">
                <span className="text-[10px] text-slate-600">{event.time}</span>
                <span className="text-slate-600">·</span>
                <span className="text-[10px] text-slate-600">AI reasoning</span>
              </div>
              <div className="mt-1 flex items-start gap-2">
                <span className="mt-0.5 text-base">{event.icon}</span>
                <div className="flex-1">
                  <p className="text-xs font-medium text-slate-200">{event.title}</p>
                  <p className="mt-1 text-[11px] leading-relaxed text-slate-500">{event.explanation}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  )
}