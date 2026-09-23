export default function Select({ label, error, options, placeholder, className = '', ...props }) {
  return (
    <label className="flex flex-col gap-1 text-left text-sm">
      {label && <span className="font-medium text-text-secondary">{label}</span>}
      <select
        className={`rounded-lg border bg-white px-3 py-2 text-text-primary focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 ${
          error ? 'border-danger' : 'border-gray-300'
        } ${className}`}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <span className="text-xs text-danger">{error}</span>}
    </label>
  )
}
