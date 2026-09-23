const VARIANTS = {
  solid: 'bg-primary text-white hover:bg-primary-dark',
  outline: 'border border-primary text-primary hover:bg-primary-light',
}

export default function Button({ children, variant = 'solid', className = '', ...props }) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-lg px-5 py-2.5 font-medium transition-colors duration-150 disabled:cursor-not-allowed disabled:opacity-50 ${VARIANTS[variant] ?? VARIANTS.solid} ${className}`}
      {...props}
    >
      {children}
    </button>
  )
}
