import { type ComponentPropsWithoutRef, forwardRef } from 'react'
import { motion, type MotionProps } from 'framer-motion'
import { cn } from '@/lib/utils'

type ButtonProps = ComponentPropsWithoutRef<'button'> & {
  variant?: 'primary' | 'secondary' | 'ghost'
} & MotionProps

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = 'primary', whileTap, transition, ...props }, ref) => (
    <motion.button
      ref={ref}
      whileTap={whileTap ?? { scale: 0.98 }}
      transition={transition ?? { duration: 0.16 }}
      className={cn(
        'inline-flex h-9 items-center justify-center rounded-lg px-3.5 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-cyan-400/70 disabled:pointer-events-none disabled:opacity-50',
        {
          'bg-cyan-400 text-slate-950 shadow-[0_0_24px_rgba(34,211,238,0.16)] hover:bg-cyan-300': variant === 'primary',
          'border border-white/10 bg-white/[0.045] text-slate-100 hover:bg-white/[0.08]': variant === 'secondary',
          'text-slate-400 hover:bg-white/[0.06] hover:text-slate-100': variant === 'ghost',
        },
        className,
      )}
      {...props}
    />
  ),
)

Button.displayName = 'Button'
