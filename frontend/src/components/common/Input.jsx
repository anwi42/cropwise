export default function Input({ label, error, className = '', ...props }) {
  return (
    <label className="flex flex-col gap-1 text-left text-sm">
      {label && <span className="font-medium text-text-secondary">{label}</span>}
      <input
        className={`rounded-lg border px-3 py-2 text-text-primary focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 ${
          error ? 'border-danger' : 'border-gray-300'
        } ${className}`}
        {...props}
      />
      {error && <span className="text-xs text-danger">{error}</span>}
    </label>
  )
}
