import { CloudSun, Droplets, Sprout } from 'lucide-react'
import { Link } from 'react-router-dom'
import Button from '../components/common/Button'
import Card from '../components/common/Card'
import Navbar from '../components/common/Navbar'

const FEATURES = [
  {
    icon: Droplets,
    title: 'Know Your Soil',
    description: 'Upload or enter your soil test report and get an instant health score.',
  },
  {
    icon: Sprout,
    title: 'Grow The Right Crop',
    description: 'AI-powered crop recommendations tailored to your soil and the season.',
  },
  {
    icon: CloudSun,
    title: 'Stay One Step Ahead',
    description: 'Get warned about dangerous weather patterns before they hit your farm.',
  },
]

export default function Landing() {
  return (
    <div className="flex min-h-screen flex-col bg-white">
      <Navbar />

      <section className="bg-primary-light px-6 py-24 text-center">
        <h1 className="mx-auto max-w-3xl text-4xl font-bold text-text-primary sm:text-5xl">
          Smart Farming Starts Here
        </h1>
        <p className="mx-auto mt-4 max-w-2xl text-lg text-text-secondary">
          AI-powered crop advisory, soil analysis, yield prediction and pest detection for
          Indian farmers
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <Link to="/register">
            <Button variant="solid" className="px-8 py-3 text-base">
              Get Started
            </Button>
          </Link>
          <a href="#features">
            <Button variant="outline" className="px-8 py-3 text-base">
              Learn More
            </Button>
          </a>
        </div>
      </section>

      <section id="features" className="mx-auto grid w-full max-w-6xl gap-6 px-6 py-16 sm:grid-cols-3">
        {FEATURES.map(({ icon: Icon, title, description }) => (
          <Card key={title} className="p-6 text-left">
            <Icon className="h-9 w-9 text-primary" />
            <h3 className="mt-4 text-lg font-semibold text-text-primary">{title}</h3>
            <p className="mt-2 text-sm text-text-secondary">{description}</p>
          </Card>
        ))}
      </section>

      <footer className="mt-auto border-t border-gray-100 py-6 text-center text-sm text-text-secondary">
        CropWise © 2026
      </footer>
    </div>
  )
}
