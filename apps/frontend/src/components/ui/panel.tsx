import { type ReactNode } from 'react'

interface PanelProps {
  children: ReactNode
  className?: string
}

export function Panel({ children, className = '' }: PanelProps) {
  return (
    <section
      className={`group relative rounded-2xl border border-white/[0.075] bg-[#0d141f]/90 shadow-[0_14px_38px_rgba(0,0,0,0.15)] transition-all duration-500 hover:-translate-y-0.5 hover:border-cyan-300/[0.16] hover:shadow-[0_20px_55px_rgba(0,0,0,0.24)] ${className}`}
    >
      {children}
    </section>
  )
}