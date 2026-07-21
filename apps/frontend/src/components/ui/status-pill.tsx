import { type ReactNode } from 'react'

type Tone = 'cyan' | 'rose' | 'amber' | 'blue' | 'emerald' | 'violet'

interface StatusPillProps {
  children: ReactNode
  tone?: Tone
}

const styles: Record<Tone, string> = {
  cyan: 'border-cyan-300/15 bg-cyan-400/[0.09] text-cyan-300',
  rose: 'border-rose-300/15 bg-rose-400/[0.09] text-rose-300',
  amber: 'border-amber-300/15 bg-amber-400/[0.09] text-amber-300',
  blue: 'border-blue-300/15 bg-blue-400/[0.09] text-blue-300',
  emerald: 'border-emerald-300/15 bg-emerald-400/[0.09] text-emerald-300',
  violet: 'border-violet-300/15 bg-violet-400/[0.09] text-violet-300',
}

export function StatusPill({ children, tone = 'cyan' }: StatusPillProps) {
  return (
    <span className={`inline-flex items-center rounded-md border px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.1em] ${styles[tone]}`}>
      {children}
    </span>
  )
}