import { Leaf } from 'lucide-react'
import { Link } from 'react-router-dom'
import Button from './Button'

export default function Navbar() {
  return (
    <header className="w-full border-b border-gray-100 bg-white">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2 text-lg font-bold text-text-primary">
          <Leaf className="h-6 w-6 text-primary" />
          CropWise
        </Link>
        <div className="flex items-center gap-3">
          <Link to="/login">
            <Button variant="outline">Login</Button>
          </Link>
          <Link to="/register">
            <Button variant="solid">Register</Button>
          </Link>
        </div>
      </div>
    </header>
  )
}
