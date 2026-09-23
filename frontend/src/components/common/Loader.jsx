export default function Loader({ label = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-8">
      <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary-light border-t-primary" />
      {label && <p className="text-sm text-text-secondary">{label}</p>}
    </div>
  )
}
