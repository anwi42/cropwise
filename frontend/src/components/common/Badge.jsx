const VARIANTS = {
  success: 'bg-success/10 text-success',
  warning: 'bg-warning/10 text-warning',
  danger: 'bg-danger/10 text-danger',
  neutral: 'bg-gray-100 text-text-secondary',
  primary: 'bg-primary-light text-primary',
}

export default function Badge({ children, variant = 'neutral', className = '' }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-semibold ${VARIANTS[variant] ?? VARIANTS.neutral} ${className}`}
    >
      {children}
    </span>
  )
}
