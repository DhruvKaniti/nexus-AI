import { 
  Bot, Satellite, Newspaper, Truck, TrendingUp, CheckCircle2, Loader2, Clock, 
  Activity, ArrowDown, Zap, Shield
} from 'lucide-react'
import { motion } from 'framer-motion'
import { Panel } from '@/components/ui/panel'
import { StatusPill } from '@/components/ui/status-pill'

interface Agent {
  name: string
  status: 'monitoring' | 'processing' | 'validating' | 'complete'
  icon: 'satellite' | 'news' | 'supply' | 'economic' | 'recommendation'
  currentTask: string
  confidence: number
  latestFinding: string
  lastUpdated: Date
}

interface AgentPipelineProps {
  agents: Agent[]
}

const agentConfig = {
  satellite: { 
    icon: Satellite, 
    color: 'cyan' as const, 
    label: 'Atlas Agent',
    description: 'Geospatial & satellite intelligence'
  },
  news: { 
    icon: Newspaper, 
    color: 'blue' as const, 
    label: 'Sentinel Agent',
    description: 'Cyber threat monitoring'
  },
  supply: { 
    icon: Truck, 
    color: 'violet' as const, 
    label: 'Supply Chain Agent',
    description: 'Global logistics & disruption'
  },
  economic: { 
    icon: TrendingUp, 
    color: 'emerald' as const, 
    label: 'Economic Agent',
    description: 'Economic impact prediction'
  },
  recommendation: { 
    icon: Bot, 
    color: 'amber' as const, 
    label: 'Recommendation Agent',
    description: 'Executive response generation'
  },
}

const statusConfig = {
  monitoring: { label: 'Monitoring', color: 'text-blue-300', bg: 'bg-blue-400/10', pulse: 'bg-blue-400' },
  processing: { label: 'Processing', color: 'text-cyan-300', bg: 'bg-cyan-400/10', pulse: 'bg-cyan-400' },
  validating: { label: 'Validating', color: 'text-violet-300', bg: 'bg-violet-400/10', pulse: 'bg-violet-400' },
  complete: { label: 'Complete', color: 'text-emerald-300', bg: 'bg-emerald-400/10', pulse: 'bg-emerald-400' },
}

export function AgentPipeline({ agents }: AgentPipelineProps) {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
  }

  const getStatusIcon = (status: Agent['status']) => {
    switch (status) {
      case 'complete':
        return <CheckCircle2 className="size-4 text-emerald-400" />
      case 'processing':
      case 'validating':
        return <Loader2 className="size-4 animate-spin text-cyan-400" />
      default:
        return <Clock className="size-4 text-slate-600" />
    }
  }

  return (
    <Panel className="p-5">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-sm font-semibold tracking-tight text-slate-100">AI Agent Pipeline</h2>
          <p className="mt-1 text-[10px] text-slate-500">Autonomous multi-agent intelligence workflow</p>
        </div>
        <StatusPill tone="emerald">
          <span className="flex items-center gap-1.5">
            <Activity className="size-3" />
            {agents.filter(a => a.status === 'complete').length}/{agents.length} Complete
          </span>
        </StatusPill>
      </div>

      {/* Agent Collaboration Flow */}
      <div className="mt-4 rounded-xl border border-white/[0.08] bg-white/[0.02] p-4">
        <div className="flex items-center gap-2 mb-3">
          <Zap className="size-3 text-amber-400" />
          <span className="text-[10px] font-semibold uppercase tracking-[0.14em] text-amber-300">Intelligence Pipeline Flow</span>
        </div>
        <div className="flex items-center justify-between">
          {agents.map((agent, index) => {
            const config = agentConfig[agent.icon]
            const status = statusConfig[agent.status]
            
            return (
              <div key={agent.name} className="flex items-center gap-2">
                <div className="flex flex-col items-center gap-1.5">
                  <div className="relative">
                    <div className={`grid size-10 place-items-center rounded-lg border ${status.bg} ${config.color === 'cyan' ? 'border-cyan-400/30 text-cyan-300' : config.color === 'blue' ? 'border-blue-400/30 text-blue-300' : config.color === 'violet' ? 'border-violet-400/30 text-violet-300' : config.color === 'emerald' ? 'border-emerald-400/30 text-emerald-300' : 'border-amber-400/30 text-amber-300'}`}>
                      <config.icon size={18} />
                    </div>
                    {(agent.status === 'processing' || agent.status === 'validating') && (
                      <motion.span
                        animate={{ scale: [1, 1.2, 1], opacity: [1, 0.7, 1] }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
                        className={`absolute -top-1 -right-1 size-2 rounded-full border-2 border-[#0d141f] ${status.pulse}`}
                      />
                    )}
                  </div>
                  <div className="text-center">
                    <p className="text-[10px] font-medium text-slate-200">{config.label}</p>
                    <p className={`text-[9px] ${status.color}`}>{status.label}</p>
                  </div>
                </div>
                {index < agents.length - 1 && (
                  <div className="flex flex-col items-center gap-0.5 px-1">
                    <ArrowDown className="size-3 text-slate-600" />
                    <span className="text-[8px] text-slate-600 max-w-[60px] text-center leading-tight">
                      {agent.status === 'complete' ? 'Passed data' : 'Waiting'}
                    </span>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>

      {/* Agent Cards */}
      <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
        {agents.map((agent) => {
          const config = agentConfig[agent.icon]
          const Icon = config.icon
          const status = statusConfig[agent.status]

          return (
            <motion.div
              key={agent.name}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="group relative overflow-hidden rounded-xl border border-white/[0.08] bg-white/[0.02] p-4 transition-all duration-300 hover:border-white/[0.15] hover:bg-white/[0.04]"
            >
              {/* Status indicator */}
              <div className="absolute top-2 right-2">
                {getStatusIcon(agent.status)}
              </div>

              {/* Icon */}
              <div className={`grid size-10 place-items-center rounded-lg ${config.color === 'cyan' ? 'bg-cyan-400/[0.1] text-cyan-300' : config.color === 'blue' ? 'bg-blue-400/[0.1] text-blue-300' : config.color === 'violet' ? 'bg-violet-400/[0.1] text-violet-300' : config.color === 'emerald' ? 'bg-emerald-400/[0.1] text-emerald-300' : 'bg-amber-400/[0.1] text-amber-300'}`}>
                <Icon size={20} />
              </div>

              {/* Name and status */}
              <div className="mt-3">
                <p className="text-xs font-medium text-slate-200">{config.label}</p>
                <p className={`mt-1 text-[10px] uppercase tracking-wider ${status.color}`}>
                  {status.label}
                </p>
              </div>

              {/* Current Task */}
              <div className="mt-3 pt-3 border-t border-white/[0.06]">
                <p className="text-[10px] text-slate-500 leading-relaxed line-clamp-2">
                  {agent.currentTask}
                </p>
              </div>

              {/* Latest Finding */}
              {agent.latestFinding && (
                <div className="mt-2.5">
                  <p className="text-[9px] font-semibold uppercase tracking-wider text-slate-600 mb-1">Latest Finding</p>
                  <p className="text-[10px] text-slate-400 leading-relaxed line-clamp-2">
                    {agent.latestFinding}
                  </p>
                </div>
              )}

              {/* Confidence & Timestamp */}
              <div className="mt-3 flex items-center justify-between pt-2.5 border-t border-white/[0.06]">
                <div className="flex items-center gap-1.5">
                  <Shield className="size-3 text-slate-600" />
                  <span className="text-[10px] font-medium text-slate-300">{agent.confidence}%</span>
                </div>
                <span className="text-[9px] text-slate-600">
                  {formatTime(agent.lastUpdated)}
                </span>
              </div>
            </motion.div>
          )
        })}
      </div>
    </Panel>
  )
}