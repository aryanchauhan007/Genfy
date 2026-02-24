"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Play, Search, Sparkles, X, Upload, Plus, Image as ImageIcon, LogOut, User as UserIcon } from "lucide-react"
import { motion, AnimatePresence } from "framer-motion"
import { useSession } from "@/contexts/session-context"
import { useRouter } from "next/navigation"
import Link from "next/link"

interface LandingPageProps {
  onCategorySelect: (category: string) => void
}

interface Category {
  name: string
  key: string
  emoji: string
  image_path: string
}

// Updated colors to match image_b07817.jpg for backgrounds
const CATEGORY_STYLES: Record<string, string> = {
  "Realistic Photo": "bg-[#E2D5C7]",
  "Stylized Art": "bg-[#F59E71]",
  "Logo": "bg-[#D4EF85]",
  "Product Shot": "bg-[#A6A6A6]",
  "Minimalist": "bg-[#C671EA]",
  "Sequential Art": "bg-[#000000]",
  "Conceptual": "bg-[#78BFD6]"
}

const FALLBACK_CATEGORIES: Category[] = [
  { name: "Realistic Photo", key: "realistic_photo", emoji: "📷", image_path: "/categories/realistic-photo.png" },
  { name: "Stylized Art", key: "stylized_art", emoji: "🎨", image_path: "/categories/stylized-art.png" },
  { name: "Logo", key: "logo_text", emoji: "✏️", image_path: "/categories/logo-text.png" },
  { name: "Product Shot", key: "product_shot", emoji: "📦", image_path: "/categories/product-shot.png" },
  { name: "Minimalist", key: "minimalist", emoji: "⚪", image_path: "/categories/minimalist.png" },
  { name: "Sequential Art", key: "sequential_art", emoji: "🎬", image_path: "/categories/sequential-art.png" },
  { name: "Conceptual", key: "conceptual", emoji: "🌀", image_path: "/categories/conceptual-abstract.png" }
]

export function LandingPage({ onCategorySelect }: LandingPageProps) {
  const [categories] = useState<Category[]>(FALLBACK_CATEGORIES)
  const [imageErrors, setImageErrors] = useState<Record<string, boolean>>({})
  const [isOverlayOpen, setIsOverlayOpen] = useState(false) // New state for overlay

  const { user, signOut } = useSession()
  const router = useRouter()

  const handleImageError = (categoryKey: string) => {
    setImageErrors(prev => ({ ...prev, [categoryKey]: true }))
  }

  const handleInteraction = (action: () => void) => {
    if (!user) {
      router.push("/auth")
    } else {
      action()
    }
  }

  // We duplicate the categories to create the seamless infinite loop
  const marqueeCategories = [...categories, ...categories]

  return (
    <div className="min-h-screen bg-white text-gray-900 font-sans selection:bg-pink-100 relative">

      {/* Navigation Bar */}
      <nav className="flex items-center justify-between px-6 py-4 sticky top-0 bg-white/90 backdrop-blur-md z-50 border-b border-transparent">
        <div className="flex items-center gap-6 flex-1">
          {/* Clicking logo closes overlay */}
          <div className="font-bold text-2xl tracking-tight cursor-pointer" onClick={() => setIsOverlayOpen(false)}>Genfy</div>

          <div className="hidden md:flex items-center bg-gray-100/80 hover:bg-gray-100 transition-colors rounded-full px-4 py-3 w-full max-w-md text-gray-500 group">
            <Search className="w-5 h-5 mr-3 text-gray-400 group-hover:text-gray-600" />
            <input
              type="text"
              placeholder="Search Poster, Logo, or anything"
              className="bg-transparent border-none outline-none text-sm w-full placeholder:text-gray-400 text-gray-900"
              onClick={() => !user && router.push("/auth")} // Redirect on focus if not logged in
            />
          </div>
        </div>

        <div className="hidden md:flex items-center gap-8 text-[15px] font-medium text-gray-600">
          <a href="#" className="hover:text-black transition-colors">Creators</a>
          <a href="#" className="hover:text-black transition-colors">Pricing</a>

          {user ? (
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 text-sm font-semibold">
                <UserIcon className="w-4 h-4" />
                {user.email?.split('@')[0]}
              </div>
              <Button
                onClick={signOut}
                variant="ghost"
                className="rounded-full px-4 py-2 hover:bg-gray-100 text-gray-600 hover:text-gray-900"
              >
                <LogOut className="w-4 h-4 mr-2" /> Sign out
              </Button>
            </div>
          ) : (
            <Link href="/auth">
              <Button className="rounded-full px-7 py-6 bg-black text-white hover:bg-gray-800 text-[15px] font-semibold transition-all hover:scale-105 active:scale-95">
                Sign In
              </Button>
            </Link>
          )}
        </div>
      </nav>

      <main className="flex flex-col items-center pt-12 pb-20 overflow-hidden w-full">

        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="text-center mb-10 max-w-4xl mx-auto px-4"
        >
          <h1 className="text-5xl md:text-7xl font-bold leading-[1.1] tracking-tight text-gray-900">
            Create{" "}
            <span className="bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 bg-clip-text text-transparent">
              anything
            </span>
            {" "}like a pro
          </h1>
        </motion.div>

        {/* --- INFINITE MARQUEE CAROUSEL --- */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="w-full py-4 mb-10"
        >
          <div className="relative w-full overflow-hidden">
            {/* The Moving Track */}
            <div
              className="flex gap-4 w-max pl-4 animate-marquee pause-on-hover scale-[1.01]" // Added scale to prevent jitter
            >
              {marqueeCategories.map((category, index) => {
                const hasImageError = imageErrors[category.key]
                const uniqueKey = `${category.key}-${index}`
                const bgColor = CATEGORY_STYLES[category.name] || "bg-gray-200"

                return (
                  <motion.button
                    key={uniqueKey}
                    onClick={() => handleInteraction(() => onCategorySelect(category.name))}

                    // Floating Wave Animation
                    animate={{ y: [0, -8, 0] }}
                    transition={{
                      y: {
                        duration: 4,
                        repeat: Infinity,
                        repeatType: "reverse",
                        ease: "easeInOut",
                        delay: index * 0.2
                      }
                    }}

                    // Hover State
                    whileHover={{
                      y: -15,
                      scale: 1.02,
                      transition: { duration: 0.2 }
                    }}
                    whileTap={{ scale: 0.98 }}

                    className={`
                      relative flex-shrink-0 w-[240px] h-[240px] rounded-[32px] 
                      ${bgColor}
                      text-left flex flex-col justify-between
                      shadow-sm hover:shadow-xl 
                      transition-shadow duration-300
                      group cursor-pointer overflow-hidden
                    `}
                  >
                    {/* Background Image */}
                    <div className="absolute inset-0 z-0">
                      {!hasImageError && category.image_path ? (
                        <img
                          src={category.image_path}
                          alt={category.name}
                          className="w-full h-full object-cover transition-transform duration-700 ease-in-out group-hover:scale-105"
                          onError={() => handleImageError(category.key)}
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center opacity-40">
                          <span className="text-8xl transition-transform duration-500 group-hover:scale-125 group-hover:rotate-6">
                            {category.emoji}
                          </span>
                        </div>
                      )}
                      {/* Original gradient to make white text pop */}
                      <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-transparent to-black/10 group-hover:to-black/30 transition-colors duration-500" />
                    </div>

                    {/* Text - RESTORED TO ORIGINAL STYLING (White, Bold, Shadow) */}
                    <div className="relative z-10 p-7">
                      <h3 className="text-[22px] font-black leading-tight text-white tracking-tight drop-shadow-md">
                        {category.name}
                      </h3>
                    </div>

                    {/* Sparkle Icon */}
                    <div className="absolute bottom-5 right-5 z-20 overflow-hidden">
                      <div className="
                        bg-white/90 backdrop-blur-sm text-black p-2.5 rounded-full shadow-lg
                        transform translate-y-12 opacity-0 
                        group-hover:translate-y-0 group-hover:opacity-100 
                        transition-all duration-500 ease-out delay-75
                        flex items-center justify-center
                      ">
                        <Sparkles className="w-4 h-4 fill-black" />
                      </div>
                    </div>

                  </motion.button>
                )
              })}
            </div>
          </div>
        </motion.div>

        {/* Buttons - Moved Below Carousel */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4 }}
          className="flex flex-wrap gap-4 justify-center items-center"
        >
          <Button
            size="lg"
            onClick={() => handleInteraction(() => setIsOverlayOpen(true))} // Updated Handler with Auth Check
            className="bg-[#1A1A1A] hover:bg-black text-white px-8 py-6 text-[15px] rounded-full font-semibold shadow-lg transition-transform hover:scale-105 active:scale-95"
          >
            Start Creating
          </Button>
          <Button size="lg" variant="outline" className="bg-white text-black border-2 border-gray-200 px-8 py-6 text-[15px] rounded-full font-bold hover:bg-gray-50 hover:text-black transition-transform hover:scale-105 active:scale-95">
            <Play className="mr-2 h-4 w-4 fill-black" /> Watch video
          </Button>
        </motion.div>
      </main>

      {/* --- OVERLAY SECTION (New Code) --- */}
      <AnimatePresence>
        {isOverlayOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-[100] bg-white/40 backdrop-blur-2xl flex flex-col items-center pt-20 px-6 overflow-y-auto"
          >
            {/* Close Button */}
            <button
              onClick={() => setIsOverlayOpen(false)}
              className="absolute top-6 right-8 p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
            >
              <X className="w-6 h-6 text-gray-600" />
            </button>

            <motion.div
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.1, duration: 0.4 }}
              className="w-full max-w-5xl flex flex-col items-center"
            >
              <h2 className="text-4xl font-bold text-gray-900 mb-8 text-center">What do you want to create today?</h2>

              {/* Search Bar in Overlay */}
              <div className="relative w-full max-w-2xl mb-8">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search Poster, Logo, or anything"
                  className="w-full bg-white border border-gray-200 rounded-full pl-12 pr-6 py-4 text-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-black/5"
                />
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 mb-12">
                <button className="flex items-center gap-2 bg-white px-6 py-3 rounded-full border border-gray-200 hover:bg-gray-50 transition-colors font-medium text-sm text-gray-700 shadow-sm">
                  <Plus className="w-4 h-4" /> Start new design
                </button>
                <button className="flex items-center gap-2 bg-white px-6 py-3 rounded-full border border-gray-200 hover:bg-gray-50 transition-colors font-medium text-sm text-gray-700 shadow-sm">
                  <Upload className="w-4 h-4" /> Upload and edit image
                </button>
              </div>

              {/* Grid Layout of Categories */}
              <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-x-6 gap-y-10 w-full">
                {categories.map((category) => {
                  const hasImageError = imageErrors[category.key]
                  return (
                    <motion.div
                      key={category.key}
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="flex flex-col items-center cursor-pointer group"
                      onClick={() => onCategorySelect(category.name)}
                    >
                      {/* Icon Box */}
                      <div className="w-20 h-20 rounded-2xl bg-gray-100 mb-3 overflow-hidden shadow-sm group-hover:shadow-md transition-shadow relative">
                        {!hasImageError && category.image_path ? (
                          <img
                            src={category.image_path}
                            alt={category.name}
                            className="w-full h-full object-cover"
                            onError={() => handleImageError(category.key)}
                          />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center bg-white text-3xl">
                            {category.emoji}
                          </div>
                        )}
                      </div>
                      {/* Label */}
                      <span className="text-sm font-medium text-gray-700 text-center group-hover:text-black">
                        {category.name}
                      </span>
                    </motion.div>
                  )
                })}

                {/* Placeholder items to fill grid visually */}
                <motion.div className="flex flex-col items-center cursor-pointer opacity-50 hover:opacity-100">
                  <div className="w-20 h-20 rounded-2xl bg-gray-100 mb-3 flex items-center justify-center">
                    <ImageIcon className="w-8 h-8 text-gray-400" />
                  </div>
                  <span className="text-sm font-medium text-gray-700">More...</span>
                </motion.div>
              </div>

            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
