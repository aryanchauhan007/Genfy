"use client"

import { useState, useEffect } from "react"
import { apiClient } from "@/lib/api-client"
import { useSession } from "@/contexts/session-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { Loader2, CheckCircle2 } from "lucide-react"

interface Category {
  name: string
  key: string
  emoji: string
  description: string
  imagepath: string
  color: string
  questioncount: number
}

interface CategorySelectorProps {
  onComplete: () => void
}

const CATEGORY_ICONS: Record<string, string> = {
  "Realistic Photo": "📷",
  "Stylized Art": "🎨",
  "Logo/Text Design": "✏️",
  "Product Shot": "📦",
  "Minimalist": "⚪",
  "Sequential Art": "🎬",
  "Conceptual/Abstract": "🌀",
}

export function CategorySelector({ onComplete }: CategorySelectorProps) {
  const [categories, setCategories] = useState<Category[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [userIdea, setUserIdea] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(true)
  const { selectCategory } = useSession()
  const { toast } = useToast()

  useEffect(() => {
    loadCategories()
  }, [])

  const loadCategories = async () => {
    setIsFetching(true)
    try {
      const response = await apiClient.getCategories()
      setCategories(response.categories)
    } catch (error) {
      console.error("Failed to load categories:", error)
      toast({
        title: "Error",
        description: "Failed to load categories. Please refresh the page.",
        variant: "destructive",
      })
    } finally {
      setIsFetching(false)
    }
  }

  const handleContinue = async () => {
    if (!selectedCategory || !userIdea.trim()) {
      toast({
        title: "Missing Information",
        description: "Please select a category and describe your idea",
        variant: "destructive",
      })
      return
    }

    if (userIdea.trim().length < 10) {
      toast({
        title: "Idea Too Short",
        description: "Please provide more details about your idea (at least 10 characters)",
        variant: "destructive",
      })
      return
    }

    setIsLoading(true)
    try {
      await selectCategory(selectedCategory, userIdea)
      toast({
        title: "Category Selected! ✨",
        description: `Ready to create your ${selectedCategory}`,
      })
      onComplete()
    } catch (error) {
      console.error("Failed to select category:", error)
      toast({
        title: "Error",
        description: "Failed to save category selection. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  if (isFetching) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-12 w-12 animate-spin text-primary" />
          <p className="text-sm text-muted-foreground">Loading categories...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="mx-auto w-full max-w-5xl space-y-8 p-6 overflow-y-auto max-h-full">
      {/* Header */}
      <div className="text-center space-y-3">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text text-transparent">
          Choose Your Creative Style
        </h1>
        <p className="text-lg text-muted-foreground">
          Select a category that matches your vision
        </p>
      </div>

      {/* Category Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {categories.map((cat) => (
          <button
            key={cat.key}
            onClick={() => setSelectedCategory(cat.name)}
            disabled={isLoading}
            className={`
              group relative p-6 rounded-2xl border-2 transition-all duration-300
              hover:scale-105 hover:shadow-xl
              ${
                selectedCategory === cat.name
                  ? "border-primary bg-primary/10 shadow-lg shadow-primary/20"
                  : "border-border hover:border-primary/50 bg-card"
              }
              disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
            `}
          >
            {/* Selected Indicator */}
            {selectedCategory === cat.name && (
              <div className="absolute -top-2 -right-2 bg-primary text-white rounded-full p-1">
                <CheckCircle2 className="h-5 w-5" />
              </div>
            )}

            {/* Icon */}
            <div className="text-5xl mb-4 transition-transform group-hover:scale-110">
              {CATEGORY_ICONS[cat.name] || cat.emoji || "🎨"}
            </div>

            {/* Category Name */}
            <h3 className="font-bold text-lg mb-2 text-foreground">
              {cat.name}
            </h3>

            {/* Description */}
            <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
              {cat.description}
            </p>

            {/* Question Count Badge */}
            <div className="flex items-center justify-center gap-2 text-xs text-muted-foreground">
              <span className="rounded-full bg-muted px-2 py-1">
                {cat.questioncount} questions
              </span>
            </div>
          </button>
        ))}
      </div>

      {/* User Idea Input */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-foreground">
          Describe Your Creative Idea
          <span className="text-destructive ml-1">*</span>
        </label>
        <Textarea
          placeholder="E.g., A futuristic cityscape at sunset with flying cars and neon lights reflecting on glass buildings..."
          value={userIdea}
          onChange={(e) => setUserIdea(e.target.value)}
          disabled={isLoading}
          className="min-h-[120px] resize-none text-base"
          maxLength={500}
        />
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span>Be as detailed as possible for better results</span>
          <span className={userIdea.length > 450 ? "text-destructive" : ""}>
            {userIdea.length} / 500
          </span>
        </div>
      </div>

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          onClick={handleContinue}
          disabled={isLoading || !selectedCategory || !userIdea.trim()}
          size="lg"
          className="w-full md:w-auto gap-2 px-8 bg-gradient-to-r from-primary to-accent text-white shadow-lg hover:shadow-xl transition-all"
        >
          {isLoading ? (
            <>
              <Loader2 className="h-5 w-5 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              Continue to Visual Settings
              <span className="text-lg">→</span>
            </>
          )}
        </Button>
      </div>
    </div>
  )
}
