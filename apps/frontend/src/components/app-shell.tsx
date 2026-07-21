import { motion } from 'framer-motion'
import { Bell, ChevronDown, LayoutDashboard, Menu, PanelLeft, Search, ShieldAlert, Waypoints, X } from 'lucide-react'
import { type ReactNode, useEffect, useState } from 'react'
import { cn } from '@/lib/utils'

const navigation = [
  { label: 'Command Center', icon: LayoutDashboard },
]

export function AppShell({ children }: { children: ReactNode }) {
  const [collapsed, setCollapsed] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)
  const [paletteOpen, setPaletteOpen] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') { event.preventDefault(); setPaletteOpen(true) }
      if (event.key === 'Escape') setPaletteOpen(false)
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  useEffect(() => {
    if (paletteOpen) {
      setSearchQuery('')
    }
  }, [paletteOpen])

  return (
    <div className="min-h-screen bg-[#090d14] text-slate-100">
      {paletteOpen && <div className="fixed inset-0 z-50 grid place-items-start bg-[#060912]/75 px-4 pt-[15vh] backdrop-blur-md" onMouseDown={() => setPaletteOpen(false)}><motion.div initial={{ opacity: 0, y: -12, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0 }} transition={{ duration: .2 }} onMouseDown={(event) => event.stopPropagation()} className="w-full max-w-xl overflow-hidden rounded-2xl border border-cyan-300/[0.16] bg-[#101925] shadow-[0_24px_80px_rgba(0,0,0,.55)]"><div className="flex items-center gap-3 border-b border-white/[0.08] px-4 py-3"><Search size={18} className="text-cyan-300" /><input autoFocus value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} placeholder="Search commands, agents, regions..." className="min-w-0 flex-1 bg-transparent text-sm text-slate-100 outline-none placeholder:text-slate-500" /><button aria-label="Close command palette" onClick={() => setPaletteOpen(false)} className="text-slate-500 hover:text-slate-300"><X size={17} /></button></div><div className="p-2"><p className="px-2 py-2 text-[10px] font-semibold uppercase tracking-[.16em] text-slate-500">Suggested actions</p>{[['Open global map', LayoutDashboard], ['Review active crises', ShieldAlert], ['Inspect AI agent activity', Waypoints]].filter(([label]) => (label as string).toLowerCase().includes(searchQuery.toLowerCase())).map(([label, Icon]) => { const ActionIcon = Icon as typeof LayoutDashboard; return <button key={label as string} onClick={() => setPaletteOpen(false)} className="flex w-full items-center gap-3 rounded-xl px-3 py-3 text-left text-sm text-slate-300 transition-colors hover:bg-cyan-400/[0.09] hover:text-cyan-200"><ActionIcon size={17} className="text-cyan-300" />{label as string}<span className="ml-auto text-[10px] text-slate-600">Enter</span></button> })}</div><div className="flex gap-4 border-t border-white/[0.07] px-4 py-2.5 text-[10px] text-slate-500"><span><kbd className="mr-1 rounded border border-white/10 px-1">↑↓</kbd> navigate</span><span><kbd className="mr-1 rounded border border-white/10 px-1">esc</kbd> close</span></div></motion.div></div>}
      {mobileOpen && <button aria-label="Close navigation" className="fixed inset-0 z-30 bg-slate-950/70 backdrop-blur-sm lg:hidden" onClick={() => setMobileOpen(false)} />}
      <aside className={cn('fixed inset-y-0 left-0 z-40 w-60 border-r border-white/[0.07] bg-[#0b1019] transition-[width,transform] duration-300 lg:z-30 lg:translate-x-0', mobileOpen ? 'translate-x-0' : '-translate-x-full', collapsed ? 'lg:w-[76px]' : 'lg:w-60')}>
        <div className="flex h-16 items-center border-b border-white/[0.07] px-4">
          <img src="/nexus-logo.svg" alt="Nexus AI" className="size-8 shrink-0" />
          {!collapsed && <span className="ml-3 text-[15px] font-semibold tracking-[0.16em] text-slate-100">NEXUS AI</span>}
        </div>
        <nav className="space-y-1 px-3 py-5">
          {navigation.map(({ label, icon: Icon }, index) => <motion.button onClick={() => setMobileOpen(false)} key={label} initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.045 }} className={cn('flex h-10 w-full items-center rounded-lg px-3 text-sm text-slate-400 transition-colors hover:bg-white/[0.045] hover:text-slate-100', index === 0 && 'bg-cyan-400/[0.09] text-cyan-300')}><Icon size={18} strokeWidth={1.8} />{!collapsed && <span className="ml-3">{label}</span>}</motion.button>)}
        </nav>
        <div className="absolute inset-x-3 bottom-4 border-t border-white/[0.07] pt-3">
          <button onClick={() => setCollapsed((value) => !value)} aria-label="Toggle sidebar" className="flex h-10 w-full items-center rounded-lg px-3 text-slate-500 hover:bg-white/[0.045] hover:text-slate-200"><PanelLeft size={18} />{!collapsed && <span className="ml-3 text-sm">Collapse</span>}</button>
        </div>
      </aside>
      <div className={cn('min-h-screen transition-[margin] duration-300', collapsed ? 'lg:ml-[76px]' : 'lg:ml-60')}>
        <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-white/[0.07] bg-[#090d14]/95 px-4 backdrop-blur sm:px-6">
          <div className="flex items-center gap-3"><button aria-label="Open navigation" onClick={() => setMobileOpen(true)} className="text-slate-400 lg:hidden"><Menu size={21} /></button><button onClick={() => setPaletteOpen(true)} className="hidden items-center gap-2 rounded-lg border border-white/[0.08] bg-white/[0.025] px-3 py-2 text-left text-sm text-slate-500 transition-colors hover:border-cyan-300/[0.16] hover:bg-white/[0.05] sm:flex"><Search size={16} /><span>Search command center</span><kbd className="ml-8 rounded border border-white/10 px-1.5 py-0.5 text-[10px]">Ctrl K</kbd></button></div>
          <div className="flex items-center gap-2"><button aria-label="Notifications" className="grid size-9 place-items-center rounded-lg text-slate-400 hover:bg-white/[0.06] hover:text-slate-100"><Bell size={18} /></button><div className="mx-1 h-6 w-px bg-white/[0.08]" /><button className="flex items-center gap-2 rounded-lg px-1.5 py-1 text-sm text-slate-300 hover:bg-white/[0.05]"><span className="grid size-7 place-items-center rounded-md bg-slate-700 text-xs font-semibold">NC</span><span className="hidden md:inline">Nexus Command</span><ChevronDown size={14} className="text-slate-500" /></button></div>
        </header>
        <main className="mx-auto w-full max-w-[1600px] p-5 sm:p-7">{children}</main>
      </div>
    </div>
  )
}
